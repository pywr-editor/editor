import pytest
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import StoragePickerWidget, FormField
from tests.utils import resolve_model_path


class TestDialogStoragePickerWidget:
    """
    Tests the ModelNodePickerWidget and StoragePickerWidget.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_storage_picker_widget.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, selected",
        [("valid_storage", "Reservoir1"), ("valid_reservoir", "Reservoir3")],
    )
    def test_valid_values(self, qtbot, model_config, param_name, selected):
        """
        Tests that the values are loaded correctly.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        assert selected_page.findChild(FormField, "name").value() == param_name

        storage_node_field: FormField = selected_page.findChild(
            FormField, "storage_node"
        )
        # noinspection PyTypeChecker
        storage_node_widget: StoragePickerWidget = storage_node_field.widget

        # check values in combobox
        for i in range(1, 4):
            assert any(
                [
                    f"Reservoir{i}" in value
                    for value in storage_node_widget.combo_box.all_items
                ]
            )
        assert storage_node_widget.get_value() == selected

        # check warning and validation
        assert storage_node_field.message.text() == ""
        output = storage_node_widget.validate(
            "", "", storage_node_widget.get_value()
        )
        assert output.validation is True

    @pytest.mark.parametrize(
        "param_name, message",
        [
            ("empty_string", ""),
            ("not_existing_name", "does not exist"),
            ("not_provided", ""),
            ("invalid_type", "is not valid"),
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

        storage_node_field: FormField = selected_page.findChild(
            FormField, "storage_node"
        )
        # noinspection PyTypeChecker
        storage_node_widget: StoragePickerWidget = storage_node_field.widget

        # check value in combobox
        assert storage_node_widget.combo_box.currentText() == "None"
        assert storage_node_widget.get_value() is None

        # check warning and validation
        assert message in storage_node_field.message.text()

        output = storage_node_widget.validate(
            "", "", storage_node_widget.get_value()
        )
        assert output.validation is False
