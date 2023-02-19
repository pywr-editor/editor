from functools import partial

import pytest
from PySide6.QtCore import QDate, Qt, QTimer
from PySide6.QtTest import QSignalSpy

from pywr_editor import MainWindow
from pywr_editor.model.pywr_worker import CaptureSolverOutput, RunMode
from pywr_editor.toolbar.run_controls.run_widget import RunWidget
from pywr_editor.widgets import DateEdit
from tests.utils import check_msg, resolve_model_path


class TestRunWidget:
    """
    Tests the widget and thread when a model is run.
    """

    def test_validate_start_end_date(self, qtbot):
        """
        Tests that an error is shown if the start date is larger than the end date.
        """
        window = MainWindow(resolve_model_path("model_1.json"))
        window.hide()

        # noinspection PyTypeChecker
        start_date_widget: DateEdit = window.findChild(DateEdit, "start_date")
        # noinspection PyTypeChecker
        end_date_widget: DateEdit = window.findChild(DateEdit, "end_date")
        # noinspection PyTypeChecker
        run_to_date_widget: DateEdit = window.findChild(DateEdit, "run_to_date")

        end_date_widget.setDate(QDate(2014, 12, 31))
        # message for run to date not triggered
        run_to_date_widget.setDate(QDate(2014, 12, 31))
        window.model_config.end_date = "2014-12-31"
        assert (
            start_date_widget.date().toPython()
            > end_date_widget.date().toPython()
        )

        # try running the model
        QTimer.singleShot(
            100,
            partial(check_msg, "The start date (01/01/2015) must be smaller"),
        )
        # noinspection PyTypeChecker
        run_widget: RunWidget = window.findChild(RunWidget)
        qtbot.mouseClick(run_widget.step_button, Qt.MouseButton.LeftButton)

    def test_validate_run_to_date(self, qtbot):
        """
        Tests that an error is shown if the start date is larger than the end date.
        """
        window = MainWindow(resolve_model_path("model_1.json"))
        window.hide()

        # noinspection PyTypeChecker
        start_date_widget: DateEdit = window.findChild(DateEdit, "start_date")
        # noinspection PyTypeChecker
        run_to_date_widget: DateEdit = window.findChild(DateEdit, "run_to_date")

        run_to_date_widget.setDate(QDate(2014, 12, 31))
        assert (
            start_date_widget.date().toPython()
            > run_to_date_widget.date().toPython()
        )

        # try running the model
        QTimer.singleShot(
            100,
            partial(check_msg, "The start date (01/01/2015) must be smaller"),
        )
        # noinspection PyTypeChecker
        run_widget: RunWidget = window.findChild(RunWidget)
        qtbot.mouseClick(run_widget.run_to_button, Qt.MouseButton.LeftButton)

    @pytest.mark.parametrize(
        "model_file",
        [
            # custom parameter fails to load
            "model_1.json",
            # solver error
            "model_solver_exception.json",
        ],
    )
    def test_loading_model_error_msg(self, qtbot, model_file):
        """
        Tests that the error message is shown if a model fails to load or run. This
        tests the Signal when the "Step" and "Run to" buttons are clicked.
        """
        window = MainWindow(resolve_model_path(model_file))
        window.hide()
        # noinspection PyTypeChecker
        run_widget: RunWidget = window.findChild(RunWidget)
        # noinspection PyTypeChecker
        run_to_date_widget: DateEdit = window.findChild(DateEdit, "run_to_date")
        run_to_date_widget.setDate(QDate(2020, 1, 1))

        # try running the model
        for button in [run_widget.step_button, run_widget.run_to_button]:
            QTimer.singleShot(
                200,
                partial(
                    check_msg,
                    "An exception occurred while running the pywr model",
                ),
            )
            qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
            spy = QSignalSpy(run_widget.worker.model_error)

            # check that the signal was emitted
            qtbot.wait(200)
            assert spy.count() == 1

    def test_step_one(self, qtbot):
        """
        Tests when the Step button is clicked.
        """
        window = MainWindow(resolve_model_path("model_to_run.json"))
        window.hide()
        # noinspection PyTypeChecker
        run_widget: RunWidget = window.findChild(RunWidget)
        run_status_changed_spy = QSignalSpy(run_widget.run_status_changed)

        # check button status before running the model
        assert run_widget.step_button.isEnabled() is True
        assert run_widget.stop_button.isEnabled() is False
        assert run_widget.run_button.isEnabled() is True
        assert run_widget.run_to_button.isEnabled() is True
        assert run_widget.inspector_action.isEnabled() is False

        # 1. Step
        qtbot.mouseClick(run_widget.step_button, Qt.MouseButton.LeftButton)
        # worker instance becomes available when model is running
        worker = run_widget.worker
        finished_spy = QSignalSpy(worker.finished)
        before_step_spy = QSignalSpy(worker.before_step)
        step_done_spy = QSignalSpy(worker.step_done)
        progress_update_spy = QSignalSpy(worker.progress_update)

        # model is running (the test is very fast and captures the instance when
        # the model is still working
        assert worker.mode == RunMode.STEP
        assert worker.is_killed is False
        assert run_widget.is_running is True

        # model has paused
        qtbot.wait(700)
        assert run_widget.step_button.isEnabled() is True
        assert run_widget.stop_button.isEnabled() is True
        assert run_widget.run_button.isEnabled() is False
        assert run_widget.run_to_button.isEnabled() is False
        assert run_widget.inspector_action.isEnabled() is True

        # check signals
        assert run_status_changed_spy.count() == 1
        assert finished_spy.count() == 0
        assert before_step_spy.count() == 1
        assert step_done_spy.count() == 1
        assert progress_update_spy.count() == 1

        # check worker status flags
        assert worker.is_killed is False
        assert worker.is_paused is True
        assert worker.mode is None

        # check schematic
        assert window.schematic.canvas.opacity != 1
        # tooltip contains the model results
        assert "Flow" in window.schematic.schematic_items["Input"].toolTip()

        # 2. Stop the model
        qtbot.mouseClick(run_widget.stop_button, Qt.MouseButton.LeftButton)

        # check worker status just before is killed
        assert worker.is_killed is True

        qtbot.wait(500)
        assert worker.pywr_model is None

        # worker and widget emits the signals
        assert run_status_changed_spy.count() == 2
        assert finished_spy.count() == 1

        assert run_widget.is_running is False

        # check buttons
        assert run_widget.run_button.isEnabled() is True
        assert run_widget.run_to_button.isEnabled() is True
        assert run_widget.step_button.isEnabled() is True
        assert run_widget.stop_button.isEnabled() is False
        assert run_widget.inspector_action.isEnabled() is False

        # schematic status and tooltip are restored
        assert window.schematic.canvas.opacity() == 1
        # tooltip contains the model results
        item = window.schematic.schematic_items["Input"]
        assert item.toolTip() == item.tooltip_text

    def test_step_until_end(self, qtbot):
        """
        Tests when the Step button is clicked and the end date is reached.
        """
        window = MainWindow(resolve_model_path("model_to_run.json"))
        window.hide()
        # noinspection PyTypeChecker
        run_widget: RunWidget = window.findChild(RunWidget)

        window.model_config.end_date = "2015-01-05"

        for _ in range(6):
            qtbot.mouseClick(run_widget.stop_button, Qt.MouseButton.LeftButton)

        # model has stopped because it run past the end date
        assert run_widget.worker is None
        assert run_widget.step_button.isEnabled() is True
        assert run_widget.stop_button.isEnabled() is False

    def test_close_editor_while_running(self, qtbot):
        """
        Tests that no exceptions are thrown when the model is running and the main
        window is closed.
        """
        window = MainWindow(resolve_model_path("model_to_run.json"))
        window.hide()
        # noinspection PyTypeChecker
        run_widget: RunWidget = window.findChild(RunWidget)

        window.model_config.end_date = "2015-01-05"

        with CaptureSolverOutput() as out:
            qtbot.mouseClick(run_widget.step_button, Qt.MouseButton.LeftButton)
            QTimer.singleShot(
                300,
                partial(check_msg, "The model has been modified"),
            )
            window.close()
        # solver does not print mem alloc message
        assert out == []
