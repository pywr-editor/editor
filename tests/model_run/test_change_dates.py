from datetime import date

import pytest
from PySide6.QtCore import QDate

from pywr_editor import MainWindow
from pywr_editor.widgets import DateEdit
from tests.utils import resolve_model_path


class TestTimeStepperWidget:
    """
    Tests that the timestepper properties are updated
    when the respective fields are changed in the
    TimeStepperWidget
    """

    @pytest.mark.parametrize(
        "field_name, expected",
        [("start_date", (2015, 1, 1)), ("end_date", (2015, 12, 31))],
    )
    def test_start_end_date(self, qtbot, field_name, expected):
        """
        Tests that the start and end date fields are correctly initialised
        and the dates are updated when the fields are changed.
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
        assert getattr(window.model_config, f"{field_name}_tuple") == (
            2016,
            8,
            19,
        )

        # set a large date
        widget.setDate(QDate(9000, 1, 1))
        assert getattr(window.model_config, field_name) == "9000-01-01"
        assert getattr(window.model_config, f"{field_name}_tuple") == (
            9000,
            1,
            1,
        )

    def test_empty_dates(self, qtbot):
        """
        Tests when the start or end date is None.
        """
        window = MainWindow(
            resolve_model_path("invalid_model_missing_props.json")
        )
        window.hide()
        # noinspection PyTypeChecker
        widget: DateEdit = window.findChild(DateEdit, "start_date")

        # check set date - widget defaults to 1/1/2000
        assert window.model_config.start_date is None
        assert window.model_config.start_date_tuple is None
        assert widget.date().toPython() == date(2000, 1, 1)
