from functools import partial

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QPushButton

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page_widget import ParameterPageWidget
from pywr_editor.form import FormField
from pywr_editor.model import ModelConfig
from tests.utils import close_message_box, resolve_model_path


class TestDialogParameterRbfSection:
    """
    Tests the validation of RbfProfileParameterSection.
    """

    model_file = resolve_model_path("model_dialog_parameters_rbf_section.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """

        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "new_values, message",
        [
            # valid
            ([89.23, 123.45, 765.12], None),
            # wrong length
            ([123, 654, 90, 90, 10], "The number of items"),
        ],
    )
    def test_check_count(self, qtbot, model_config, new_values, message):
        """
        Tests the check_count validation method.
        """
        param_name = "rbf_param"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        values_field: FormField = selected_page.findChild(FormField, "values")
        assert selected_page.findChild(FormField, "name").value() == param_name

        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")
        # button is disabled
        assert save_button.isEnabled() is False

        # 1. Set new value
        new_values_str = list(map(str, new_values))
        new_values_str = ",".join(new_values_str)
        values_field.widget.line_edit.setText(new_values_str)

        assert save_button.isEnabled() is True

        # 2. Validate
        # ignore failed validation messages
        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        if message is None:
            assert values_field.message.text() == ""
            assert model_config.has_changes is True
            model_param_dict = {
                "type": "rbfprofile",
                "days_of_year": [1, 30, 50],
                "values": new_values,
            }
            assert model_config.parameters.config(param_name) == model_param_dict
        else:
            assert message in values_field.message.text()

    @pytest.mark.parametrize(
        "field_name, new_value, message",
        [
            # valid
            ("days_of_year", [1, 89, 100], None),
            # first day must be one
            ("days_of_year", [5, 9, 10], "The first item must be 1"),
            # length < 3
            ("days_of_year", [1, 65], "at least 3 items"),
            # not increasing
            ("days_of_year", [1, 100, 65], "monotonically increasing"),
            # outside bounds
            ("days_of_year", [1, 300, 400], "between 1 and 365"),
            # valid variable_days_of_year_range
            ("variable_days_of_year_range", 6, None),
            # invalid variable_days_of_year_range
            (
                "variable_days_of_year_range",
                50,
                "the distance between this value",
            ),
        ],
    )
    def test_check_day_of_year(
        self, qtbot, model_config, field_name, new_value, message
    ):
        """
        Tests the check_day_of_year validation method.
        """
        param_name = "rbf_param"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form
        days_field = form.find_field(field_name)
        assert form.find_field("name").value() == param_name

        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")
        # button is disabled
        assert save_button.isEnabled() is False

        # 1. Set new value
        if field_name == "days_of_year":
            new_values_str = list(map(str, new_value))
            new_values_str = ",".join(new_values_str)
            days_field.widget.line_edit.setText(new_values_str)
        else:
            days_field.widget.setValue(new_value)

        assert save_button.isEnabled() is True

        # 2. Validate
        # ignore failed validation messages
        QTimer.singleShot(100, partial(close_message_box, form))
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        if message is None:
            assert days_field.message.text() == ""
            assert model_config.has_changes is True
            if field_name == "days_of_year":
                model_param_dict = {
                    "type": "rbfprofile",
                    "days_of_year": new_value,
                    "values": [3.2, 7, 4.3],
                }
            else:
                model_param_dict = {
                    "type": "rbfprofile",
                    "days_of_year": [1, 30, 50],
                    "variable_days_of_year_range": new_value,
                    "values": [3.2, 7, 4.3],
                }
            assert model_config.parameters.config(param_name) == model_param_dict
        else:
            assert message in days_field.message.text()
