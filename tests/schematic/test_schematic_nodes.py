import pytest
from typing import Tuple
from PySide6.QtCore import Qt, QPoint
from pywr_editor import MainWindow
from pywr_editor.model import ModelConfig
from pywr_editor.schematic import (
    Schematic,
    SchematicItem,
    Edge,
    DeleteNodeCommand,
)
from pywr_editor.toolbar.tab_panel import TabPanel
from tests.utils import resolve_model_path


class TestSchematicNodes:
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

    @staticmethod
    def is_node_deleted(
        model_config: ModelConfig,
        node_name: str,
        schematic: Schematic,
        removed_edges: list[Edge],
    ) -> None:
        """
        Checks that a node and its edges are deleted.
        :param model_config: The ModelConfig instance.
        :param node_name: The node that was removed.
        :param schematic: The Schematic instance.
        :param removed_edges: The list of Edge instance that were removed.
        :return: None
        """
        # 1. Check node and edges
        # the node is removed from the model configuration
        assert model_config.nodes.find_node_index_by_name(node_name) is None

        # node is removed from the items list
        assert node_name not in schematic.schematic_items.keys()

        # node is removed from the schematic as graphical item
        node_names = [
            node.name
            for node in schematic.items()
            if isinstance(node, SchematicItem)
        ]
        assert node_name not in node_names

        # 2. Check edges
        # the node edges are removed from the model configuration
        for edge in model_config.edges.get_all():
            assert node_name not in edge

        # the edges are removed from the schematic as graphical items
        all_edges = [
            edge for edge in schematic.items() if isinstance(edge, Edge)
        ]
        for removed_edge in removed_edges:
            assert removed_edge not in all_edges

        # the edges are removed from the lists of source and target nodes
        all_connected_node_names = [edge.source.name for edge in all_edges] + [
            edge.target.name for edge in all_edges
        ]
        assert node_name not in all_connected_node_names

        # node is deleted from the component tree
        tree_nodes = schematic.app.components_tree.items["nodes"]
        for group in range(tree_nodes.childCount()):
            for child_id in range(tree_nodes.child(group).childCount()):
                assert node_name not in tree_nodes.child(group).child(
                    child_id
                ).text(0)

    def test_delete_node(self, qtbot, init_window) -> None:
        """
        Tests that the nodes are properly deleted from the schematic and the model
        configuration.
        """
        node_name = "Link2"
        window, schematic, node_op_panel = init_window
        model_config = schematic.model_config
        original_node_config = model_config.nodes.get_node_config_from_name(
            node_name
        )
        original_edges = [
            edge for edge in model_config.edges.get_all() if node_name in edge
        ]

        node = schematic.schematic_items[node_name]
        removed_edges = node.edges
        node.on_delete_node()

        assert model_config.has_changes is True

        # 1. Check node and edges
        self.is_node_deleted(
            model_config=model_config,
            node_name=node_name,
            schematic=schematic,
            removed_edges=removed_edges,
        )

        # 2. Test undo operation
        assert window.undo_stack.canUndo() is True
        undo_command: DeleteNodeCommand = window.undo_stack.command(0)

        # check internal status
        assert undo_command.deleted_node_configs == {
            node_name: original_node_config
        }
        assert sorted(undo_command.deleted_edges) == sorted(original_edges)

        # undo
        undo_command.undo()

        # node is restored
        assert model_config.nodes.find_node_index_by_name(node_name) is not None
        assert node_name in schematic.schematic_items.keys()
        node_names = [
            node.name
            for node in schematic.items()
            if isinstance(node, SchematicItem)
        ]
        assert node_name in node_names

        # edges are restored
        assert sorted(original_edges) == sorted(
            [
                [name, node_name]
                for name in model_config.edges.get_sources(node_name)
            ]
            + [
                [node_name, name]
                for name in model_config.edges.get_targets(node_name)
            ]
        )

        # check edges in schematic
        all_schematic_edges = [
            [edge.source.name, edge.target.name]
            for edge in schematic.items()
            if isinstance(edge, Edge)
        ]

        for edge in original_edges:
            assert edge in all_schematic_edges

        # check node internal connections
        assert model_config.edges.get_sources(node_name) == [
            item.name
            for item in schematic.schematic_items[node_name].connected_nodes[
                "source_nodes"
            ]
        ]
        assert model_config.edges.get_targets(node_name) == [
            item.name
            for item in schematic.schematic_items[node_name].connected_nodes[
                "target_nodes"
            ]
        ]

        # 3. Test redo operation
        # get new schematic item instance
        node = schematic.schematic_items[node_name]
        removed_edges = node.edges

        undo_command.redo()
        self.is_node_deleted(
            model_config=model_config,
            node_name=node_name,
            schematic=schematic,
            removed_edges=removed_edges,
        )

    def test_delete_nodes(self, qtbot, init_window) -> None:
        """
        Tests that multiple selected nodes are properly deleted.
        """
        window, schematic, node_op_panel = init_window
        model_config = schematic.model_config
        nodes_to_delete = ["Reservoir", "Link3"]
        deleted_schematic_edge_dict = {}
        original_node_config_dict = {
            node_name: model_config.nodes.get_node_config_from_name(node_name)
            for node_name in nodes_to_delete
        }
        original_edges = [
            edge
            for edge in model_config.edges.get_all()
            for node_name in nodes_to_delete
            if node_name in edge
        ]

        # 1. Select 3 nodes
        for node in nodes_to_delete:
            schematic_item = schematic.schematic_items[node]
            schematic_item.setSelected(True)
            deleted_schematic_edge_dict[node] = schematic_item.edges

        # delete them
        panel = window.toolbar.tabs["Nodes"].panels["Operations"]
        qtbot.mouseClick(panel.buttons["Delete"], Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True

        for node_name in nodes_to_delete:
            self.is_node_deleted(
                model_config=model_config,
                node_name=node_name,
                schematic=schematic,
                removed_edges=deleted_schematic_edge_dict[node_name],
            )

        # edges to already existing nodes have been deleted
        assert model_config.edges.get_all() == [
            ["Link1", "Link2"],
            ["Link2", "Link4"],
        ]

        # 3. Undo operation
        assert window.undo_stack.canUndo() is True
        undo_command: DeleteNodeCommand = window.undo_stack.command(0)
        assert undo_command.deleted_node_configs == original_node_config_dict
        assert sorted(undo_command.deleted_edges) == sorted(original_edges)

        # undo
        undo_command.undo()

        # nodes are restored
        all_restored_edges = []
        node_names = [
            node.name
            for node in schematic.items()
            if isinstance(node, SchematicItem)
        ]
        all_schematic_edges = [
            [edge.source.name, edge.target.name]
            for edge in schematic.items()
            if isinstance(edge, Edge)
        ]
        for node_name in nodes_to_delete:
            assert (
                model_config.nodes.find_node_index_by_name(node_name)
                is not None
            )
            assert node_name in schematic.schematic_items.keys()
            assert node_name in node_names

            # check edges in schematic
            for edge in original_edges:
                assert edge in all_schematic_edges

            # check node internal connections
            sources = model_config.edges.get_sources(node_name)
            sources = [] if sources is None else sources
            all_restored_edges += [[name, node_name] for name in sources]

            targets = model_config.edges.get_targets(node_name)
            targets = [] if targets is None else targets
            all_restored_edges += [[node_name, name] for name in targets]
            assert sources == [
                item.name
                for item in schematic.schematic_items[
                    node_name
                ].connected_nodes["source_nodes"]
            ]
            assert targets == [
                item.name
                for item in schematic.schematic_items[
                    node_name
                ].connected_nodes["target_nodes"]
            ]

        # all edges are restored
        assert sorted(original_edges) == sorted(all_restored_edges)

        # 4. Test redo operation
        # get new schematic item instance
        for node_name in nodes_to_delete:
            schematic_item = schematic.schematic_items[node_name]
            deleted_schematic_edge_dict[node_name] = schematic_item.edges

        undo_command.redo()
        for node_name in nodes_to_delete:
            self.is_node_deleted(
                model_config=model_config,
                node_name=node_name,
                schematic=schematic,
                removed_edges=deleted_schematic_edge_dict[node_name],
            )

    def test_connect_node(self, qtbot, init_window):
        """
        Tests when a node is connected to another one.
        """
        window, schematic, node_op_panel = init_window
        model_config = schematic.model_config

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
            if isinstance(node, SchematicItem) and node.name == "Link3":
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

        assert model_config.edges.get_targets("Link3") == [
            "Link2",
            "Reservoir",
        ]
