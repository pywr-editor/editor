from datetime import date

import pytest
from PySide6.QtCore import QDate, Qt, QTimer
from PySide6.QtWidgets import QWidget

from pywr_editor import MainWindow
from pywr_editor.toolbar.run_controls.run_widget import RunWidget
from pywr_editor.widgets import DateEdit, SpinBox
from tests.utils import close_message_box, resolve_model_path


class TestTimeStepperWidget:
    """
    Tests that the timestepper properties are updated when the respective fields are
    changed in the TimeStepperWidget.
    """

    @pytest.mark.parametrize(
        "field_name, expected",
        [("start_date", (2015, 1, 1)), ("end_date", (2015, 12, 31))],
    )
    def test_start_end_date(self, qtbot, field_name, expected):
        """
        Tests that the start and end date fields are correctly initialised and the
        dates are updated when the fields are changed.
        """
        window = MainWindow(resolve_model_path("model_1.json"))
        window.hide()

        # noinspection PyTypeChecker
        widget: DateEdit = window.findChild(DateEdit, field_name)

        # check set date
        assert widget.date().toPython() == date(*expected)

        # change the date
        widget.setDate(QDate(2016, 8, 19))
        assert window.model_config.has_changes is True
        assert getattr(window.model_config, field_name) == "2016-08-19"

        # set a large date
        widget.setDate(QDate(9000, 1, 1))
        assert getattr(window.model_config, field_name) == "9000-01-01"

    def test_empty_dates(self, qtbot):
        """
        Tests when the start or end date is None.
        """
        QTimer.singleShot(400, close_message_box)
        window = MainWindow(
            resolve_model_path("invalid_model_missing_props.json")
        )
        window.hide()
        # noinspection PyTypeChecker
        widget: DateEdit = window.findChild(DateEdit, "start_date")

        # check set date - widget defaults to 1/1/2000
        assert window.model_config.start_date is None
        assert widget.date().toPython() == date(2000, 1, 1)

    def test_empty_run_to_date(self, qtbot):
        """
        Tests when the run-tp date is None.
        """
        QTimer.singleShot(400, close_message_box)
        window = MainWindow(resolve_model_path("model_2.json"))
        window.hide()
        # noinspection PyTypeChecker
        end_date_widget: DateEdit = window.findChild(DateEdit, "end_date")
        # noinspection PyTypeChecker
        run_to_date_widget: DateEdit = window.findChild(DateEdit, "run_to_date")

        assert window.editor_settings.run_to_date is None
        assert (
            run_to_date_widget.date().toPython()
            == end_date_widget.date().toPython()
        )

    def test_timestep(self, qtbot):
        """
        Tests that the timestep field is correctly initialised and it is updated when
        the field is changed.
        """
        QTimer.singleShot(400, close_message_box)
        window = MainWindow(resolve_model_path("model_1.json"))
        window.hide()
        # noinspection PyTypeChecker
        widget: SpinBox = window.findChild(SpinBox, "time_step")

        assert window.model_config.time_delta == 1

        widget.setValue(4)
        assert widget.value() == 4
        assert window.model_config.time_delta == 4

    def test_timestepper_status_while_running(self, qtbot):
        """
        Tests that all the timestepper fields are disabled when the model is running.
        """
        window = MainWindow(resolve_model_path("model_to_run.json"))
        window.hide()

        # noinspection PyTypeChecker
        run_widget: RunWidget = window.findChild(RunWidget)

        # noinspection PyTypeChecker
        timestepper_widgets: list[QWidget] = [
            window.findChild(DateEdit, name)
            for name in ["start_date", "end_date", "run_to_date"]
        ]
        # noinspection PyTypeChecker
        timestepper_widgets.append(window.findChild(SpinBox, "time_step"))

        assert all([w.isEnabled() for w in timestepper_widgets]) is True

        # run the model
        qtbot.mouseClick(run_widget.step_button, Qt.MouseButton.LeftButton)
        qtbot.wait(200)
        assert all([w.isEnabled() for w in timestepper_widgets]) is False

        # stop it
        qtbot.mouseClick(run_widget.stop_button, Qt.MouseButton.LeftButton)
        qtbot.wait(200)
        assert all([w.isEnabled() for w in timestepper_widgets]) is True
