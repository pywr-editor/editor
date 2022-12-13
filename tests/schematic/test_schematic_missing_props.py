import pytest
from PySide6.QtCore import QTimer
from pywr_editor import MainWindow
from pywr_editor.model import Constants
from tests.utils import resolve_model_path, close_message_box


class TestMissingSchematicProps:
    model_file = resolve_model_path("model_missing_schematic_props.json")

    @pytest.fixture
    def window(self) -> MainWindow:
        """
        Initialises the window.
        :return: The window instance.
        """
        QTimer.singleShot(100, close_message_box)
        window = MainWindow(self.model_file)
        window.hide()

        return window

    def test_missing_schematic_size(self, qtbot, window):
        """
        Tests that the schematic size defaults to the default value when it is missing
        in the configuration file.
        """
        assert (
            window.model_config.schematic_size
            == Constants.DEFAULT_SCHEMATIC_SIZE.value
        )

    def test_missing_node_position(self, qtbot, window):
        """
        Tests that nodes with missing positions are assigned the default position.
        """
        schematic = window.schematic
        # node with missing editor_position key
        assert schematic.schematic_items["Link1"].scenePos().toTuple() == (
            window.schematic.schematic_width / 2,
            window.schematic.schematic_height / 2,
        )

        # node with missing position key
        assert schematic.schematic_items["Link2"].scenePos().toTuple() == (
            window.schematic.schematic_width / 2,
            window.schematic.schematic_height / 2,
        )

        # node with empty editor_position list
        assert schematic.schematic_items["Link3"].scenePos().toTuple() == (
            window.schematic.schematic_width / 2,
            window.schematic.schematic_height / 2,
        )
