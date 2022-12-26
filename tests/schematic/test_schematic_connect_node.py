from typing import Tuple

import pytest
from PySide6.QtCore import QPoint, Qt

from pywr_editor import MainWindow
from pywr_editor.schematic import Edge, Schematic, SchematicNode
from pywr_editor.schematic.commands.connect_node_command import (
    ConnectNodeCommand,
)
from pywr_editor.toolbar.tab_panel import TabPanel
from tests.utils import resolve_model_path


class TestSchematicConnectNodes:
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
        node_op_panel = window.toolbar.tabs["Nodes"].panels["Operations"]

        return window, schematic, node_op_panel

    def test_connect_node(self, qtbot, init_window):
        """
        Tests when a node is connected to another one.
        """
        window, schematic, node_op_panel = init_window
        model_config = schematic.model_config
        panel = schematic.app.toolbar.tabs["Nodes"].panels["Undo"]
        undo_button = panel.buttons["Undo"]
        redo_button = panel.buttons["Redo"]

        # 1. Connect two nodes
        # select Link3
        source_point = schematic.mapFromScene(QPoint(50, 500))
        qtbot.mouseMove(schematic, source_point, -1)
        qtbot.mouseClick(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.NoModifier,
            source_point,
        )
        found = False
        for node in schematic.items():
            if isinstance(node, SchematicNode) and node.name == "Link3":
                found = True
                assert node.isSelected() is True
        assert found is True

        # enable connect mode
        qtbot.mouseClick(
            node_op_panel.buttons["Connect"], Qt.MouseButton.LeftButton
        )

        # select the target node Reservoir
        target_point = schematic.mapFromScene(QPoint(200, 500))
        qtbot.mouseMove(schematic.viewport(), target_point, -1)
        qtbot.mouseClick(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.NoModifier,
            target_point,
        )

        # 2. Check model changes
        assert model_config.has_changes is True
        assert model_config.edges.get_targets("Link3") == [
            "Link2",
            "Reservoir",
        ]

        # 3. Check init of command
        undo_command: ConnectNodeCommand = window.undo_stack.command(0)

        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False
        assert undo_command.source_node.name == "Link3"
        assert undo_command.target_node.name == "Reservoir"
        assert undo_command.edge_config is None

        # add slot to test the new edge config is restored later
        edge, ei = model_config.edges.find_edge("Link3", "Reservoir")
        edge.append(1)

        # 4. Undo command
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True
        assert undo_command.edge_config == ["Link3", "Reservoir", 1]
        assert model_config.edges.find_edge("Link3", "Reservoir") == (
            None,
            None,
        )

        # check internal Edges in schematic nodes
        assert len(schematic.schematic_items["Link3"].edges) == 1
        assert len(schematic.schematic_items["Reservoir"].edges) == 1

        # check edge item in schematic
        all_schematic_edges = [
            [edge.source.name, edge.target.name]
            for edge in schematic.items()
            if isinstance(edge, Edge)
        ]

        assert ["Link3", "Reservoir"] not in all_schematic_edges

        # 5. Redo command
        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False

        # edge is restored
        assert model_config.edges.find_edge("Link3", "Reservoir")[0] == [
            "Link3",
            "Reservoir",
            1,
        ]

        # check internal Edges in schematic nodes
        assert len(schematic.schematic_items["Link3"].edges) == 2
        assert len(schematic.schematic_items["Reservoir"].edges) == 2

        # check edge item in schematic
        all_schematic_edges = [
            [edge.source.name, edge.target.name]
            for edge in schematic.items()
            if isinstance(edge, Edge)
        ]

        assert ["Link3", "Reservoir"] in all_schematic_edges

        # 6. Undo, rename connected node and redo
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        model_config.nodes.rename("Reservoir", "Lake")

        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)

        # command becomes obsolete and edge is not restored
        assert model_config.edges.find_edge("Link3", "Lake")[0] is None
        assert model_config.edges.find_edge("Link3", "Reservoir")[0] is None

        # buttons are disabled
        qtbot.wait(400)  # setObsolete is delayed by the command
        assert redo_button.isEnabled() is False
        assert undo_button.isEnabled() is False

        # command object is deleted and not accessible anymore
        with pytest.raises(RuntimeError):
            assert undo_command.isObsolete() is True
