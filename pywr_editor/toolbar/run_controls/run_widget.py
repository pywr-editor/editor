from datetime import datetime
from typing import TYPE_CHECKING

import pandas as pd
from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtGui import QAction, QIcon, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from pywr_editor.dialogs import InspectorDialog
from pywr_editor.model import PywrProgress, PywrWorker
from pywr_editor.style import Color, stylesheet_dict_to_str
from pywr_editor.toolbar.small_button import ToolbarSmallButton
from pywr_editor.utils import Logging
from pywr_editor.widgets import DateEdit

if TYPE_CHECKING:
    from pywr_editor import MainWindow

"""
 Widget used to control a model
 run using pywr.
"""


class RunWidget(QWidget):
    run_status_changed = Signal(bool)
    """ Signal emitted when the run status changes. It returns True when
    the model is running, False otherwise """

    def __init__(self, parent: "MainWindow"):
        """
        Initialises the widget.
        :param parent: The parent widget.
        """
        super().__init__()
        self.app = parent
        self.logger = Logging().logger(self.__class__.__name__)
        self.model_config = parent.model_config
        self.inspector_action = parent.actions.get("run-inspector")
        self.inspector_action.triggered.connect(self.open_inspector)

        # Worker
        self.worker: PywrWorker | None = None
        self.thread: QThread | None = None
        self.is_running = False

        # Control buttons
        action_obj = QAction(
            icon=QIcon(":toolbar/run"), text="Run", parent=parent
        )
        # noinspection PyUnresolvedReferences
        action_obj.triggered.connect(self.run_to)
        action_obj.setToolTip("Run the model until the end date")
        self.run_button = ToolbarSmallButton(action=action_obj, parent=self)

        action_obj = QAction(
            icon=QIcon(":toolbar/run-to"), text="Run to", parent=parent
        )
        # noinspection PyUnresolvedReferences
        action_obj.triggered.connect(self.run_to)
        action_obj.setToolTip("Run the model to the 'Run to' date")
        self.run_to_button = ToolbarSmallButton(action=action_obj, parent=self)

        action_obj = QAction(
            icon=QIcon(":toolbar/step"), text="Step", parent=parent
        )
        # noinspection PyUnresolvedReferences
        action_obj.triggered.connect(self.step)
        action_obj.setToolTip("Run the model by one timestep")
        self.step_button = ToolbarSmallButton(action=action_obj, parent=self)

        action_obj = QAction(
            icon=QIcon(":toolbar/stop"), text="Stop", parent=parent
        )
        # noinspection PyUnresolvedReferences
        action_obj.triggered.connect(self.stop)
        action_obj.setToolTip("Stop the model run")
        self.stop_button = ToolbarSmallButton(action=action_obj, parent=self)
        self.stop_button.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.run_to_button)
        button_layout.addWidget(self.step_button)
        button_layout.addWidget(self.stop_button)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.progress_bar.setStyleSheet(self.progress_bar_style)
        self.progress_status = QLabel("Ready to run")
        self.progress_status.setMinimumWidth(70)

        progress_layout = QHBoxLayout()
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_status)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(50)
        main_layout.addLayout(progress_layout)

        self.setLayout(main_layout)

    @property
    def progress_bar_style(self) -> str:
        """
        Returns the progress bar style.
        :return: The style as string.
        """
        return stylesheet_dict_to_str(
            {
                "QProgressBar": {
                    "background": "white",
                    "border": f"1px solid {Color('neutral', 300).hex}",
                    "border-radius": "5px",
                    "height": "10px",
                    "text-align": "center",
                    "::chunk": {"background-color": Color("blue", 400).hex},
                }
            }
        )

    def run_worker(self) -> bool | None:
        """
        Starts the worker and thread process.
        :return: Whether the worker was started or None if the worker is already
        running.
        """
        if self.is_running:
            self.logger.debug("Worker is already running")
            return

        if not self.validate_timestepper():
            return False

        self.logger.debug("Starting a new worker")
        self.worker = PywrWorker(
            model_dict=self.model_config.json,
            model_file=self.model_config.json_file,
        )
        self.thread = QThread(self)
        self.worker.moveToThread(self.thread)

        # noinspection PyUnresolvedReferences
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.run_done)

        self.worker.before_step.connect(self.before_step)
        self.worker.step_done.connect(self.step_done)
        self.worker.before_run_to.connect(self.before_run_to)
        self.worker.run_to_done.connect(self.run_to_done)

        self.worker.progress_update.connect(self.update_progress)
        self.worker.status_update.connect(self.update_status)

        self.worker.model_load_error.connect(self.on_model_error)

        self.thread.start()
        self.is_running = True

        return True

    @Slot()
    def run_done(self) -> None:
        """
        Slot called when the run is completed (i.e. the thread is killed
        or the run completes when the thread exits normally).
        :return: None
        """
        self.logger.debug("Run done")
        self.is_running = False
        self.run_status_changed.emit(False)
        self.thread.exit()

        self.run_button.setEnabled(True)
        self.run_to_button.setEnabled(True)
        self.step_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.inspector_action.setEnabled(False)

    @Slot()
    def before_step(self) -> None:
        """
        Handles the button status when the step button is clicked.
        :return: None
        """
        self.run_button.setEnabled(False)
        self.run_to_button.setEnabled(False)
        self.step_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.inspector_action.setEnabled(False)

    @Slot()
    def step_done(self) -> None:
        """
        Handles the button status when the timestep is advanced.
        :return: None
        """
        self.step_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.inspector_action.setEnabled(True)
        self.run_status_changed.emit(True)

    @Slot()
    def before_run_to(self) -> None:
        """
        Handles the button status when the Run to button is clicked.
        :return: None
        """
        self.run_button.setEnabled(False)
        self.run_to_button.setEnabled(False)
        self.step_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.inspector_action.setEnabled(False)

    @Slot()
    def run_to_done(self) -> None:
        """
        Handles the button status when the model is run until the Run to date.
        :return: None
        """
        self.step_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.inspector_action.setEnabled(True)
        self.run_status_changed.emit(True)

    @Slot()
    def step(self) -> None:
        """
        Increase the timestep.
        :return: None
        """
        if self.run_worker() is False:
            return
        self.worker.step()

    @Slot()
    def run_to(self) -> None:
        """
        Runs the model until the Run to date.
        :return: None
        """
        # validate run-to date before run_worker()
        if not self.validate_run_to():
            return

        if self.run_worker() is False:
            return

        # noinspection PyTypeChecker
        run_to_widget: DateEdit = self.app.findChild(DateEdit, "run_to_date")
        self.worker.run_to(
            date=pd.Timestamp(run_to_widget.date().toString("yyyy-MM-dd"))
        )

    @Slot()
    def stop(self) -> None:
        """
        Kills the thread.
        :return: None
        """
        self.logger.debug("Stopping thread")
        self.progress_bar.reset()
        self.progress_status.setText("Ready to run")
        self.worker.kill()

    @Slot(PywrProgress)
    def update_progress(self, progress_data: PywrProgress) -> None:
        """
        Updates the progress bar and label.
        :param progress_data: The progress data from the thread.
        :return: None
        """
        per = progress_data["current_index"] / progress_data["last_index"] * 100
        if per == 100:
            self.progress_bar.reset()
            self.progress_status.setText("")
        else:
            self.progress_bar.setValue(per)
            self.progress_status.setText(
                progress_data["current_timestamp"].strftime("%d/%m/%Y")
            )

    @Slot(str)
    def update_status(self, message: str) -> None:
        """
        Updates the run status.
        :param message: The status description.
        :return: None
        """
        self.progress_status.setText(message)

    @Slot(str)
    def on_model_error(self, exception: str) -> None:
        """
        Shows an error dialog with the exception if the model fails to load.
        :param exception: The exception message.
        :return: None
        """
        message = QMessageBox()
        message.setWindowTitle("Model error")
        message.setIcon(QMessageBox.Icon.Critical)
        message.setText(
            "An exception occurred while trying to load the pywr model. "
            + "The complete stack trace has been reported below. "
        )
        message.setDetailedText(exception)
        message.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        # open thr exception message box
        for button in message.buttons():
            if message.buttonRole(button) == QMessageBox.ButtonRole.ActionRole:
                button.click()
                break
        message.exec()

    @Slot()
    def open_inspector(self) -> None:
        """
        Opens the run inspector dialog.
        :return: None
        """
        dialog = InspectorDialog(
            model_config=self.model_config, pywr_model=self.worker.pywr_model
        )
        dialog.show()

    def validate_timestepper(self) -> bool:
        """
        Checks that the timestep dates are properly configured and valid.
        :return: True if the timestepper dates are valid, False otherwise.
        # noinspection PyUnresolvedReferences
        """
        # noinspection PyUnresolvedReferences
        start_date: datetime = (
            self.app.findChild(DateEdit, "start_date").date().toPython()
        )
        # noinspection PyUnresolvedReferences
        end_date: datetime = (
            self.app.findChild(DateEdit, "end_date").date().toPython()
        )

        if start_date >= end_date:
            self.app.on_error_message(
                f"The start date ({start_date.strftime('%d/%m/%Y')}) must be smaller "
                + f"than the end date ({end_date.strftime('%d/%m/%Y')}). Please make "
                + "sure that the date fields are properly configured",
                False,
                "Cannot run the model",
            )
            return False

        return True

    def validate_run_to(self) -> bool:
        """
        Checks that the timestep dates are properly configured and valid.
        :return: True if the timestepper dates are valid, False otherwise.
        # noinspection PyUnresolvedReferences
        """
        # noinspection PyUnresolvedReferences
        start_date: datetime = (
            self.app.findChild(DateEdit, "start_date").date().toPython()
        )
        # noinspection PyUnresolvedReferences
        run_to_date: datetime = (
            self.app.findChild(DateEdit, "run_to_date").date().toPython()
        )

        if start_date >= run_to_date:
            self.app.on_error_message(
                f"The start date ({start_date.strftime('%d/%m/%Y')}) must be smaller "
                + f"than the end date ({run_to_date.strftime('%d/%m/%Y')}). Please "
                + "make sure that the date fields are properly configured",
                False,
                "Cannot run the model",
            )
            return False

        return True
