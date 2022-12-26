from typing import Tuple

import pytest
from PySide6 import QtCore, QtGui
from PySide6.QtCore import QEvent, QMimeData, QObject, QPoint
from PySide6.QtGui import QDragEnterEvent, Qt
from PySide6.QtWidgets import QWidget

from pywr_editor import MainWindow
from pywr_editor.schematic import Edge, Schematic, SchematicNode
from pywr_editor.schematic.commands.add_node_command import AddNodeCommand
from pywr_editor.toolbar.tab_panel import TabPanel
from tests.utils import resolve_model_path


class EventFilter(QObject):
    def eventFilter(self, obj: QWidget, event: QEvent):
        super().eventFilter(obj, event)
        return False


class TestAddNodes:
    model_file = resolve_model_path("model_1.json")

    @pytest.fixture
    def init_window(self) -> Tuple[MainWindow, Schematic, TabPanel]:
        """
        Initialises the window.
        :return: A tuple with the window, schematic and tab panel instances.
        """
        window = MainWindow(self.model_file)
        window.hide()
        schematic = window.schematic
        node_lib_panel = window.toolbar.tabs["Nodes"].panels["Nodes Library"]

        return window, schematic, node_lib_panel

    def test_drag_drop_node_to_schematic(self, qtbot, init_window) -> None:
        """
        Tests that when a node is dropped onto the schematic, the node is correctly
        added to the model and the schematic. This only tests the dragEnterEvent and
        dropEvent methods in the Schematic class.
        """
        window, schematic, _ = init_window
        model_config = schematic.model_config
        item_count = len(schematic.node_items)
        panel = schematic.app.toolbar.tabs["Nodes"].panels["Undo"]
        undo_button = panel.buttons["Undo"]
        redo_button = panel.buttons["Redo"]

        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is False

        # 1. Drop a link node
        mime_data = QMimeData()
        mime_data.setText("Link")

        # start the drop event
        scene_pos = QPoint(100, 50)
        event = QDragEnterEvent(
            scene_pos,
            Qt.DropAction.CopyAction,
            mime_data,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        QtCore.QCoreApplication.sendEvent(schematic.viewport(), event)

        # drop the node
        event = QtGui.QDropEvent(
            scene_pos,
            Qt.DropAction.MoveAction,
            mime_data,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            QEvent.Drop,
        )
        QtCore.QCoreApplication.sendEvent(schematic.viewport(), event)

        # 2. Check that the new node is in the schematic
        new_item_count = len(schematic.node_items)
        new_node_name = list(schematic.node_items.keys())[-1]
        assert new_item_count == item_count + 1
        assert "Node " in list(schematic.node_items.keys())[-1]

        assert model_config.has_changes is True
        # the node is in the model configuration
        assert (
            model_config.nodes.find_node_index_by_name(new_node_name)
            is not None
        )
        # the node dictionary is correct
        node_dict = model_config.nodes.get_node_config_from_name(new_node_name)
        node_pos = schematic.mapToScene(scene_pos).toTuple()

        assert node_dict["name"] == new_node_name
        assert node_dict["type"] == "Link"
        assert node_dict["position"]["editor_position"][0] == round(
            node_pos[0], 4
        )
        assert node_dict["position"]["editor_position"][1] == round(
            node_pos[1], 4
        )

        # 3. Check undo action
        undo_command: AddNodeCommand = window.undo_stack.command(0)

        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False
        assert undo_command.node_config.props == node_dict

        # connect new edge and rename
        new_edge = ["Reservoir", new_node_name, 0]
        model_config.edges.add(*new_edge)
        schematic.scene.addItem(
            Edge(
                source=schematic.node_items["Reservoir"],
                target=schematic.node_items[new_node_name],
            )
        )
        new_new_node_name = "New link"
        model_config.nodes.rename(new_node_name, new_new_node_name)

        schematic.reload()
        assert node_dict["name"] == new_new_node_name
        new_edge[1] = new_new_node_name

        # undo
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True

        # node and edges are removed from model config
        assert model_config.nodes.find_node_index_by_name(new_node_name) is None
        assert (
            model_config.nodes.find_node_index_by_name(new_new_node_name)
            is None
        )
        edge, _ = model_config.edges.find_edge(*new_edge[0:2])
        assert edge is None
        assert undo_command.deleted_edges[0] == new_edge

        # node and edges are removed from schematic
        assert new_node_name not in schematic.node_items.keys()
        assert new_new_node_name not in schematic.node_items.keys()
        node_names = [
            node.name
            for node in schematic.items()
            if isinstance(node, SchematicNode)
        ]
        assert new_node_name not in node_names
        assert new_new_node_name not in node_names
        all_schematic_edges = [
            [edge.source.name, edge.target.name]
            for edge in schematic.items()
            if isinstance(edge, Edge)
        ]
        assert new_edge[0:2] not in all_schematic_edges

        # 4. Check redo action
        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False

        # node and edges are restored in the model configuration
        assert (
            model_config.nodes.get_node_config_from_name(new_new_node_name)
            == node_dict
        )
        edge, _ = model_config.edges.find_edge(*new_edge[0:2])
        assert edge == new_edge
        assert undo_command.deleted_edges[0] == new_edge

        # node and edges are restored from schematic
        assert new_new_node_name in schematic.node_items.keys()
        node_names = [
            node.name
            for node in schematic.items()
            if isinstance(node, SchematicNode)
        ]
        assert new_new_node_name in node_names
        all_schematic_edges = [
            [edge.source.name, edge.target.name]
            for edge in schematic.items()
            if isinstance(edge, Edge)
        ]
        assert new_edge[0:2] in all_schematic_edges
