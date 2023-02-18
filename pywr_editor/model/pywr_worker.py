import gc
import traceback
from enum import Enum
from typing import TypedDict

from pandas import Timestamp
from PySide6.QtCore import QMutex, QObject, QWaitCondition, Signal
from pywr.model import Model

from pywr_editor.utils import Logging


class RunMode(Enum):
    STEP = 0
    """ Run Model.step() """
    RUN_TO = 1
    """ Run Model.step() in a loop """
    RUN = 2
    """ Run Model.run() """


class PywrProgress(TypedDict):
    current_timestamp: Timestamp
    """ Current model timestamp as pywr.Timestamp instance """
    current_index: int
    """ Current timestep index """
    last_index: int
    """ Last index of the run """


class PywrWorker(QObject):
    progress_update = Signal(PywrProgress)
    """ Signal with the dictionary containing the information for the current step """
    status_update = Signal(str)
    """ Signal emitted when the run status is updated """
    before_step = Signal()
    """ Signal emitted just before the worker runs Model.step() """
    step_done = Signal()
    """ The worker has run Model.step() """
    before_run_to = Signal()
    """ Signal emitted just before the worker runs Model.step() in loop to reach the
    'Run to' date """
    run_to_done = Signal()
    """ The worker has run the model up to the provided date """
    finished = Signal()
    """ Signal emitted when the worker has finished running and it instance is not
    needed anymore """
    model_load_error = Signal(str)
    """ Signal emitted when the model fails to load """

    def __init__(self, model_config: dict, model_folder: str):
        """
        Initialises the worker to run the pywr model.
        :param model_config: The dictionary containing the model.
        :param model_folder: The absolute path to the model file. This is used
        to let pywr resolve relative files in the JSON file.
        """
        super().__init__()
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug("Init thread")

        self.mode: RunMode | None = None
        self.model_config = model_config
        self.model_folder = model_folder
        self.run_to_date: Timestamp | None = None
        self.pywr_model: Model | None = None

        self.is_paused = False
        self.is_killed = False
        self.paused_cond = QWaitCondition()
        self.mutex = QMutex()

    def run(self) -> None:
        """
        Runs the model.
        :return: None
        """
        # Load the model first and check if it fails
        # noinspection PyBroadException
        try:
            self.logger.debug("Loading model")
            self.status_update.emit("Loading model")
            # noinspection PyArgumentList
            self.pywr_model: Model = Model.load(
                data=self.model_config, path=self.model_folder
            )
            # noinspection PyUnresolvedReferences
            last_index = len(self.pywr_model.timestepper) - 1
        except Exception:
            e = traceback.format_exc()
            self.logger.debug(f"Pywr failed to load because: {e}")
            self.model_load_error.emit(e)
            self.finished.emit()
            return

        # start the worker loop
        current_timestep = None
        while self.is_killed is False:
            # stop the thread when the last timestep has been reached
            if current_timestep and (current_timestep.index >= last_index):
                self.logger.debug("Last timestep reached")
                self.kill()
                break

            # pause the thread loop
            self.mutex.lock()
            if self.is_paused:
                self.paused_cond.wait(self.mutex)
            self.mutex.unlock()

            if self.mode == RunMode.STEP:
                self.before_step.emit()
                self.logger.debug("Stepping")
                self.pywr_model.step()
                # noinspection PyUnresolvedReferences
                current_timestep = self.pywr_model.timestepper.current

                self.logger.debug(
                    f"Stepped to {current_timestep} ({current_timestep.index+1}"
                    + f"/{last_index+1})"
                )
                self.step_done.emit()
                self.progress_update.emit(
                    PywrProgress(
                        current_timestamp=current_timestep.period.to_timestamp(),
                        current_index=current_timestep.index,
                        last_index=last_index,
                    )
                )
                self.pause()
            elif self.mode == RunMode.RUN_TO and self.run_to_date:
                self.logger.debug(f"Running to {self.run_to_date}")
                self.before_run_to.emit()

                # run the model until the Run to date or the end of the run is reached
                while not (
                    current_timestep
                    and (
                        (current_timestep.index >= last_index)
                        or current_timestep.period.to_timestamp()
                        >= self.run_to_date
                    )
                ):
                    self.pywr_model.step()
                    # noinspection PyUnresolvedReferences
                    current_timestep = self.pywr_model.timestepper.current
                    self.progress_update.emit(
                        PywrProgress(
                            current_timestamp=current_timestep.period.to_timestamp(),
                            current_index=current_timestep.index,
                            last_index=last_index,
                        )
                    )
                self.logger.debug(
                    f"Run to {current_timestep} ({current_timestep.index+1}"
                    + f"/{last_index+1})"
                )
                self.run_to_done.emit()

                self.pause()

        del self.pywr_model
        gc.collect()
        self.finished.emit()
        self.pywr_model = None

    def pause(self) -> None:
        """
        Pauses the worker loop and resets its status.
        :return: None
        """
        self.mutex.lock()
        self.is_paused = True
        self.mode = None
        self.run_to_date = None
        self.mutex.unlock()

    def resume(self) -> None:
        """
        Resumes the thread execution.
        :return: None
        """
        self.mutex.lock()
        self.is_paused = False
        self.mode = None
        self.mutex.unlock()
        self.paused_cond.wakeAll()

    def step(self) -> None:
        """
        Increase the model timestep by one. This resumes
        the thread if it was previously paused.
        :return: None
        """
        if self.is_paused:
            self.resume()

        self.mutex.lock()
        self.mode = RunMode.STEP
        self.mutex.unlock()

    def run_to(self, date: Timestamp) -> None:
        """
        Runs the model until the provided date.
        :param date: The date to run the model to.
        :return: None
        """
        if self.is_paused:
            self.resume()

        self.mutex.lock()
        self.mode = RunMode.RUN_TO
        self.run_to_date = date
        self.mutex.unlock()

    def kill(self) -> None:
        """
        Stops the thread.
        :return: None
        """
        if self.is_paused:
            self.resume()

        self.mutex.lock()
        self.is_killed = True
        self.mutex.unlock()
