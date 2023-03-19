import pytest

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import FormField, ThresholdValuesWidget
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogThresholdValuesWidget:
    """
    Tests the ThresholdValuesWidget.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_threshold_values_widget.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, values", [("valid_values", [1.432, 53.033])]
    )
    def test_valid_values(self, qtbot, model_config, param_name, values):
        """
        Tests that the values are loaded correctly.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        assert selected_page.findChild(FormField, "name").value() == param_name

        values_field: FormField = selected_page.findChild(FormField, "values")
        values_widget: ThresholdValuesWidget = values_field.widget

        assert values_field.message.text() == ""

        # check values in boxes
        for si, spin_box in enumerate(values_widget.spin_boxes):
            assert spin_box.value() == values[si]

        # check returned value by the widget
        assert values_widget.get_value() == values

    @pytest.mark.parametrize(
        "param_name, message",
        [
            # with None or empty list, no warning is shown
            # ("empty_values", ""),
            ("values_not_provided", ""),
            ("one_value", "must contains two values"),
            ("three_values", "must contains two values"),
            ("invalid_string", "is not valid"),
            ("invalid_number", "is not valid"),
        ],
    )
    def test_invalid_values(self, qtbot, model_config, param_name, message):
        """
        Tests that the warning message is shown when the values are not valid.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        assert selected_page.findChild(FormField, "name").value() == param_name

        values_field: FormField = selected_page.findChild(FormField, "values")
        values_widget: ThresholdValuesWidget = values_field.widget

        # check values in boxes
        for si, spin_box in enumerate(values_widget.spin_boxes):
            assert spin_box.value() == 0.0
        # check returned value by the widget
        assert values_widget.get_value() == [0.0, 0.0]

        # check warning
        assert message in values_field.message.text()
