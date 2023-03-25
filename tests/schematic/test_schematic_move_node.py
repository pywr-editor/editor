from typing import Tuple

import pytest
from PySide6.QtCore import QPoint, Qt

from pywr_editor import MainWindow
from pywr_editor.schematic import Schematic
from pywr_editor.schematic.commands.move_item_command import MoveItemCommand
from pywr_editor.toolbar.tab_panel import TabPanel
from tests.utils import resolve_model_path


class TestSchematicMoveNodes:
    model_file = resolve_model_path("model_delete_nodes.json")

    @pytest.fixture
    def init_window(self) -> Tuple[MainWindow, Schematic, TabPanel]:
        """
        Initialises the window.
        :return: A tuple with the window, schematic and tab panel instances.
        """
        window = MainWindow(self.model_file)
        window.hide()
        schematic = window.schematic
        node_op_panel = window.toolbar.tabs["Operations"].panels["Operations"]

        return window, schematic, node_op_panel

    def test_move_node(self, qtbot, init_window):
        """
        Tests that, when a node is moved, its new position is saved.
        """
        window, schematic, node_op_panel = init_window
        model_config = schematic.model_config
        panel = schematic.app.toolbar.tabs["Operations"].panels["Undo"]
        undo_button = panel.buttons["Undo"]
        redo_button = panel.buttons["Redo"]
        node_name = "Link3"

        # 1. Move Link3
        node_item = schematic.node_items[node_name]
        initial_pos = node_item.position
        assert node_item.prev_position == initial_pos
        new_pos = QPoint(150, 100)

        # mock drag and drop
        node_item.setPos(new_pos)
        node_item.setSelected(True)
        command = MoveItemCommand(
            schematic=schematic,
            selected_items=schematic.scene.selectedItems(),
        )
        window.undo_stack.push(command)

        # check that node was moved
        assert node_item.scenePos() == new_pos
        assert node_item.position == new_pos.toTuple()
        assert (
            model_config.nodes.get_node_config_from_name(
                node_name, as_dict=False
            ).position
            == new_pos.toTuple()
        )

        # 2. Check init of undo command
        undo_command: MoveItemCommand = window.undo_stack.command(0)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False
        assert undo_command.prev_positions == [initial_pos]
        assert undo_command.updated_positions == [new_pos.toTuple()]

        # 3. Undo action
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True

        node_item = schematic.node_items[node_name]
        assert node_item.scenePos().toTuple() == initial_pos
        assert node_item.position == initial_pos
        assert (
            model_config.nodes.get_node_config_from_name(
                node_name, as_dict=False
            ).position
            == initial_pos
        )

        # 3. Redo
        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False

        node_item = schematic.node_items[node_name]
        assert node_item.scenePos() == new_pos
        assert node_item.position == new_pos.toTuple()
        assert (
            model_config.nodes.get_node_config_from_name(
                node_name, as_dict=False
            ).position
            == new_pos.toTuple()
        )
