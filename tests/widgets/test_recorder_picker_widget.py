import pytest

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import FormField, ModelRecorderPickerWidget
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogModelRecorderPickerWidget:
    """
    Tests the ModelRecorderPickerWidget.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_recorder_picker_widget.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    def test_valid_values(self, qtbot, model_config):
        """
        Tests that the values are loaded correctly.
        """
        param_name = "valid"
        selected = "Recorder1"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        assert selected_page.findChild(FormField, "name").value() == param_name

        recorder_field: FormField = selected_page.findChild(FormField, "recorder")
        # noinspection PyTypeChecker
        recorder_widget: ModelRecorderPickerWidget = recorder_field.widget

        # check values in combobox
        assert recorder_widget.combo_box.all_items == ["None"] + [
            f"Recorder{i}" for i in range(1, 3)
        ]
        assert recorder_widget.get_value() == selected

        # check warning and validation
        assert recorder_field.message.text() == ""
        output = recorder_widget.validate("", "", recorder_widget.get_value())
        assert output.validation is True

    @pytest.mark.parametrize(
        "param_name, message",
        [
            ("empty_string", ""),
            ("not_existing_name", "does not exist"),
            ("not_provided", ""),
        ],
    )
    def test_invalid_values(self, qtbot, model_config, param_name, message):
        """
        Tests that the warning message is shown when the value passed to the widget
        is not valid.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        assert selected_page.findChild(FormField, "name").value() == param_name

        recorder_field: FormField = selected_page.findChild(FormField, "recorder")
        # noinspection PyTypeChecker
        recorder_widget: ModelRecorderPickerWidget = recorder_field.widget

        # check value in combobox
        assert recorder_widget.combo_box.currentText() == "None"
        assert recorder_widget.get_value() == "None"

        # check warning and validation
        assert message in recorder_field.message.text()

        output = recorder_widget.validate("", "", recorder_widget.get_value())
        assert output.validation is False
