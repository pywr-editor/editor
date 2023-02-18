from functools import partial

from PySide6.QtCore import QDate, Qt, QTimer

from pywr_editor import MainWindow
from pywr_editor.toolbar.run_controls.run_widget import RunWidget
from pywr_editor.widgets import DateEdit
from tests.utils import check_msg, resolve_model_path


class TestRunWidget:
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
            600,
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
            600,
            partial(check_msg, "The start date (01/01/2015) must be smaller"),
        )
        # noinspection PyTypeChecker
        run_widget: RunWidget = window.findChild(RunWidget)
        qtbot.mouseClick(run_widget.run_to_button, Qt.MouseButton.LeftButton)
