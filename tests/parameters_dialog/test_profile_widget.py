import pytest
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QPushButton
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import MonthlyValuesWidget, FormField
from tests.utils import resolve_model_path


# delay test otherwise this may fail when run with GitHub actions
@pytest.mark.usefixtures("delay")
class TestDialogParameterProfileWidget:
    """
    Tests the ProfileWidget used to define a profile on a parameter.
    """

    model_file = resolve_model_path(
        "model_dialog_parameters_monthly_profile.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    def test_valid_parameter(self, qtbot, model_config):
        """
        Tests that the form is correctly loaded.
        """
        param_name = "valid_monthly_profile_param"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        value_field: FormField = selected_page.findChild(FormField, "values")
        value_widget: MonthlyValuesWidget = value_field.widget
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )

        # 1. Test value
        assert selected_page.findChild(FormField, "name").value() == param_name
        assert value_field.message.text() == ""
        current_values = list(range(10, 130, 10))
        current_values = [c + 0.1 for c in current_values]
        assert value_field.value() == current_values
        assert save_button.isEnabled() is False

        # 2. Change value
        table = value_widget.table

        x = table.columnViewportPosition(1) + 5
        y = table.rowViewportPosition(0) + 10
        current_values[0] = 5.0
        # Double-clicking the table cell to set it into editor mode does not work.
        # Click->Double Click works, however
        qtbot.mouseClick(
            table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
        )
        qtbot.mouseDClick(
            table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
        )
        qtbot.keyClick(table.viewport().focusWidget(), Qt.Key_5)
        qtbot.keyClick(table.viewport().focusWidget(), Qt.Key_Enter)

        # wait to let the model update itself
        qtbot.wait(0.1)
        assert value_widget.model.values == current_values
        assert value_field.value() == current_values
        # button is enabled
        assert save_button.isEnabled() is True

        # 3. Test reset
        value_widget.reset()
        assert value_field.value() == [0] * 12

    @pytest.mark.parametrize(
        "param_name, message",
        [
            ("invalid_size_monthly_profile_param", "number of values set"),
            ("invalid_type_monthly_profile_param", "must be all numbers"),
        ],
    )
    def test_invalid_parameter(self, qtbot, model_config, param_name, message):
        """
        Tests that the form displays a warning message when the provided value is
        invalid.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        value_field: FormField = selected_page.findChild(FormField, "values")

        assert selected_page.findChild(FormField, "name").value() == param_name
        assert message in value_field.message.text()
        assert value_field.value() == [0] * 12
