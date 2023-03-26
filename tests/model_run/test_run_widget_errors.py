from functools import partial

import pytest
from PySide6.QtCore import QDate, Qt, QTimer
from PySide6.QtTest import QSignalSpy

from pywr_editor import MainWindow
from pywr_editor.model.pywr_worker import CaptureSolverOutput
from pywr_editor.toolbar.run_controls.run_widget import RunWidget
from pywr_editor.widgets import DateEdit
from tests.utils import check_msg, resolve_model_path


class TestRunWidgetErrors:
    """
    Tests error handling in run widget.
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
        Tests that an error is shown if the start date is larger than the end date
        or the end date is smaller the the run-to date.
        """
        window = MainWindow(resolve_model_path("model_1.json"))
        window.hide()

        # noinspection PyTypeChecker
        start_date_widget: DateEdit = window.findChild(DateEdit, "start_date")
        # noinspection PyTypeChecker
        end_date_widget: DateEdit = window.findChild(DateEdit, "end_date")
        # noinspection PyTypeChecker
        run_to_date_widget: DateEdit = window.findChild(DateEdit, "run_to_date")

        # 1. Test the start date
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

        # 2. Test the end date
        run_to_date_widget.setDate(QDate(2020, 12, 31))
        assert (
            run_to_date_widget.date().toPython()
            > end_date_widget.date().toPython()
        )

        # try running the model
        QTimer.singleShot(
            100,
            partial(check_msg, "The run-to date (31/12/2020) must be smaller"),
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
        run_to_date_widget.setDate(QDate(2015, 7, 1))

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

            # progress status is reset
            assert "Ready" in run_widget.progress_status.text()

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
