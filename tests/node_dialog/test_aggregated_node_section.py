import pytest
from PySide6.QtCore import Qt, QTimer
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import NodeDialog
from pywr_editor.form import TableValuesWidget
from tests.utils import resolve_model_path, close_message_box


class TestAggregatedNodeSection:
    """
    Tests the validation and filter of AggregatedNodeSection.
    """

    model_file = resolve_model_path("model_dialog_node.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    def test_validate_weights(
        self,
        qtbot,
        model_config,
    ):
        """
        Tests the validate method for the weights.
        """
        node_name = "aggregated_node"
        dialog = NodeDialog(model_config=model_config, node_name=node_name)
        dialog.hide()

        form = dialog.form
        save_button = form.save_button
        widget: TableValuesWidget = form.find_field_by_name(
            "flow_weights"
        ).widget

        # set one weight, validation fails
        widget.model.values[0] = [1.9]

        save_button.setEnabled(True)
        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert (
            "When you provide the weight for at least one node"
            in widget.form_field.message.text()
        )

        # set two weights, validation passes
        new_weights = [1.9, 5]
        widget.model.values[0] = new_weights
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert widget.form_field.message.text() == ""
        assert (
            model_config.nodes.get_node_config_from_name(node_name)[
                "flow_weights"
            ]
            == new_weights
        )

        # set no weights, validation passes
        widget.model.values[0] = []
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert widget.form_field.message.text() == ""
        assert (
            "flow_weights"
            not in model_config.nodes.get_node_config_from_name(node_name)
        )
