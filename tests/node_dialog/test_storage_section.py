import pytest
from functools import partial
from PySide6.QtCore import Qt, QTimer
from pywr_editor.model import ModelConfig, ParameterConfig
from pywr_editor.dialogs import NodeDialog
from tests.utils import resolve_model_path, check_msg


class TestStorageSection:
    """
    Tests the AbstractStorageSection and StorageSection.
    """

    model_file = resolve_model_path("model_dialog_node_storage_section.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    def test_validate_section(
        self,
        qtbot,
        model_config,
    ):
        """
        Tests the validate method in AbstractStorageSection.
        """
        dialog = NodeDialog(model_config=model_config, node_name="Reservoir")
        dialog.hide()

        form = dialog.form
        save_button = form.save_button

        initial_volume = form.find_field_by_name("initial_volume")
        initial_volume_pc = form.find_field_by_name("initial_volume_pc")
        max_volume = form.find_field_by_name("max_volume")

        # both initial volumes are empty
        save_button.setEnabled(True)
        error_message = "must provide the initial absolute or relative volume"

        QTimer.singleShot(100, partial(check_msg, error_message))
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        # set both fields
        initial_volume.widget.line_edit.setText("10")
        initial_volume_pc.widget.line_edit.setText("0.3")
        error_message = "can only provide on type of initial volume"
        QTimer.singleShot(100, partial(check_msg, error_message))
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        # set both fields - set max_volume as constant
        max_volume.widget.component_obj = ParameterConfig(
            {"type": "constant", "value": 1000}
        )
        assert max_volume.value() == 1000
        error_message = "can only provide on type of initial volume"
        QTimer.singleShot(100, partial(check_msg, error_message))
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        # set one type of initial volume - no errors
        initial_volume.widget.reset()
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        # set max_volume as parameter (string) with one type of initial volume
        max_volume.widget.component_obj = ParameterConfig(
            {"type": "monthlyprofile", "value": list(range(0, 11))}
        )
        error_message = (
            "must provide both the initial absolute and relative volume"
        )
        QTimer.singleShot(100, partial(check_msg, error_message))
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
