import pytest
from PySide6.QtCore import QTimer
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import RecordersDialog
from pywr_editor.dialogs.recorders.recorder_page_widget import (
    RecorderPageWidget,
)
from pywr_editor.form import DayMonthWidget
from tests.utils import resolve_model_path, close_message_box


class TestDayMonthWidget:
    """
    Tests the DayMonthWidget.
    """

    model_file = resolve_model_path(
        "model_dialog_recorders_day_month_widget.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "recorder_name, expected_dict, validation_message",
        [
            # day and month not provided
            (
                "not_set",
                {
                    "day": 0,
                    "month": 0,
                },
                None,
            ),
            # valid values
            (
                "valid",
                {
                    "day": 21,
                    "month": 5,
                },
                None,
            ),
        ],
    )
    def test_valid_recorder(
        self,
        qtbot,
        model_config,
        recorder_name,
        expected_dict,
        validation_message,
    ):
        """
        Tests when the widget contains valid data.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form
        field = form.find_field_by_name("include_from")
        widget: DayMonthWidget = field.widget

        # 1. Check message and value
        assert field.message.text() == ""

        # check value returned by the widget
        assert field.value() == expected_dict

        # 2. Validate form
        QTimer.singleShot(100, close_message_box)
        form_data = form.validate()

        if validation_message is not None:
            assert validation_message in field.message.text()
        # validate form and test section filter
        else:
            expected_form_data = {
                "name": recorder_name,
                "type": "annualcountindexthreshold",
                "parameters": ["param1", "param2"],
                "threshold": 1,
                "include_from_month": expected_dict["month"],
                "include_from_day": expected_dict["day"],
            }
            if expected_dict == widget.get_default_value():
                del expected_form_data["include_from_day"]
                del expected_form_data["include_from_month"]

            assert form_data == expected_form_data

        # 3. Test reset
        widget.reset()
        assert widget.get_value() == widget.get_default_value()

    @pytest.mark.parametrize(
        "recorder_name, init_message",
        [
            ("invalid_missing_month", "must provide the month"),
            ("invalid_missing_day", "must provide the day"),
            ("invalid_day_too_large", "must be a number between 1 and 31"),
            ("invalid_month_too_large", "must be a number between 1 and 12"),
        ],
    )
    def test_invalid_recorder(
        self,
        qtbot,
        model_config,
        recorder_name,
        init_message,
    ):
        """
        Tests when the widget contains invalid data.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form
        field = form.find_field_by_name("include_from")
        widget: DayMonthWidget = field.widget

        # check message and values
        assert init_message in field.message.text()
        assert widget.get_value() == widget.get_default_value()
