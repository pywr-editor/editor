from typing import Tuple

import pytest
from PySide6.QtGui import QAction, Qt

from pywr_editor import MainWindow
from pywr_editor.model import Edges
from pywr_editor.schematic import Edge, Schematic
from pywr_editor.schematic.commands.disconnect_node_command import DisconnectNodeCommand
from pywr_editor.toolbar.tab_panel import TabPanel
from tests.utils import resolve_model_path


class TestDeleteEdges:
    model_file = resolve_model_path("model_delete_edges.json")

    @pytest.fixture
    def init_window(self) -> Tuple[MainWindow, Schematic, TabPanel]:
        """
        Initialises the window.
        :return: A tuple with the window, schematic and tab panel instances.
        """
        window = MainWindow(self.model_file)
        window.hide()
        schematic = window.schematic
        size_panel = window.toolbar.tabs["Schematic"].panels["Size"]

        return window, schematic, size_panel

    def test_delete_edge_from_source_node(self, qtbot, init_window) -> None:
        """
        Tests that the edges are properly deleted from the schematic and the model
        configuration.
        """
        window, schematic, size_panel = init_window
        model_config = schematic.model_config
        panel = schematic.app.toolbar.tabs["Operations"].panels["Undo"]
        undo_button = panel.buttons["Undo"]
        redo_button = panel.buttons["Redo"]

        source_node = schematic.node_items["Reservoir"]
        target_node = schematic.node_items["Link1"]  # target is Link1

        # 1. Disconnect the nodes
        dummy_action = QAction()
        dummy_action.setData({"source_node": source_node, "target_node": target_node})
        source_node.on_disconnect_edge(dummy_action)

        # edge must not be in the model dict anymore
        assert Edges(model_config).targets(source_node.name) == ["Link2"]

        # source node has one edge left (to Link2)
        assert len(source_node.edges) == 1

        # target node Link1 is connected to Link2 only
        assert target_node.edges == [schematic.node_items["Link2"].edges[1]]

        # edge is gone from schematic
        all_schematic_edges = []
        for item in schematic.items():
            if isinstance(item, Edge):
                all_schematic_edges.append([item.source.name, item.target.name])
        assert ["Reservoir", "Link1"] not in all_schematic_edges

        assert model_config.has_changes is True

        # 2. Check init of undo command
        undo_command: DisconnectNodeCommand = window.undo_stack.command(0)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False
        assert undo_command.source_node.name == "Reservoir"
        assert undo_command.target_node.name == "Link1"
        assert undo_command.edge_config == ["Reservoir", "Link1"]

        # 3. Undo command
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True

        # the edge is restore in model config
        assert model_config.edges.find("Reservoir", "Link1")[0] is not None

        # the edge is restored on schematic
        all_schematic_edges = []
        for item in schematic.items():
            if isinstance(item, Edge):
                all_schematic_edges.append([item.source.name, item.target.name])
        assert ["Reservoir", "Link1"] in all_schematic_edges

        # 4. Redo, rename connected node and undo
        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)
        model_config.nodes.rename("Reservoir", "Lake")

        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)

        # command becomes obsolete and edge is not restored
        assert model_config.edges.find("Lake", "Link1")[0] is None
        assert model_config.edges.find("Reservoir", "Link1")[0] is None

        # command object is deleted and not accessible anymore
        with pytest.raises(RuntimeError):
            assert undo_command.isObsolete() is True

        # buttons are disabled
        assert redo_button.isEnabled() is False
        assert undo_button.isEnabled() is False
