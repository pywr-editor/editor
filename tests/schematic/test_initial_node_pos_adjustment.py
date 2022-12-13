import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from pywr_editor.schematic import SchematicNodeUtils
from pywr_editor import MainWindow
from tests.utils import resolve_model_path


class TestInitialWrongPosition:
    model_file = resolve_model_path("wrong_initial_pos_model_1.json")
    dialog_text = None

    @pytest.fixture
    def window(self) -> MainWindow:
        """
        Initialises the window.
        :return: The window instance.
        """
        QTimer.singleShot(100, self.get_warning_message)
        # QTimer.singleShot(100, close_message_box)
        window = MainWindow(self.model_file)
        window.hide()

        return window

    def get_warning_message(self) -> None:
        """
        Saves the text in the warning message.
        :return: None
        """
        widget = QApplication.activeModalWidget()
        self.dialog_text = widget.text()
        widget.close()

    def test_node_outside_left_edge(self, qtbot, window):
        """
        Tests that if a node is initially outside the schematic canvas, the node is
        moved to the correct position and the user is warned about the change.
        """
        schematic = window.schematic

        item = schematic.schematic_items["Link"]
        item_utils = SchematicNodeUtils(
            node=item,
            schematic_size=[
                schematic.schematic_width,
                schematic.schematic_height,
            ],
        )
        assert item_utils.is_outside_left_edge is False
        assert item.sceneBoundingRect().left() == 0.0

        item = schematic.schematic_items["Output"]
        item_utils = SchematicNodeUtils(
            node=item,
            schematic_size=[
                schematic.schematic_width,
                schematic.schematic_height,
            ],
        )

        assert item_utils.is_outside_left_edge is False
        assert item.sceneBoundingRect().bottom() == schematic.schematic_height
        assert "2 nodes were outside" in self.dialog_text
