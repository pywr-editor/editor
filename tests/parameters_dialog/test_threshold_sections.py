import pytest

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import Form, FormField
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogThresholdSection:
    """
    Tests the sections for the threshold parameters.
    """

    model_file = resolve_model_path("model_dialog_parameter_threshold_sections.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, expected",
        [
            (
                "storage_threshold",
                {
                    "type": "StorageThreshold",
                    "threshold": 23,
                    "values": [1.432, 53.033],
                    "predicate": "EQ",
                    "storage_node": "Reservoir1",
                },
            ),
            (
                "node_threshold",
                {
                    "type": "NodeThreshold",
                    "threshold": 23,
                    "values": [1.432, 53.033],
                    "predicate": "EQ",
                    "node": "Output",
                },
            ),
            (
                "parameter_threshold",
                {
                    "type": "ParameterThreshold",
                    "threshold": 23,
                    "values": [1.432, 53.033],
                    "predicate": "EQ",
                    "parameter": "monthly_profile",
                },
            ),
            (
                "recorder_threshold",
                {
                    "type": "RecorderThreshold",
                    "threshold": 23,
                    "values": [1.432, 53.033],
                    "predicate": "EQ",
                    "recorder": "Recorder1",
                },
            ),
        ],
    )
    def test_valid_values(self, qtbot, model_config, param_name, expected):
        """
        Tests that the values are loaded correctly.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        assert selected_page.findChild(FormField, "name").value() == param_name

        # check for warnings
        for field in selected_page.findChildren(FormField):
            field: FormField
            assert field.message.text() == ""

        form = selected_page.findChild(Form)
        form_data = form.validate()
        del form_data["name"]

        # check returned dictionary
        expected["type"] = expected["type"].lower()
        assert form_data == expected
