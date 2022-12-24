from typing import Tuple

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from pywr_editor import MainWindow
from pywr_editor.model import ModelConfig
from pywr_editor.schematic import (
    DeleteNodeCommand,
    Edge,
    Schematic,
    SchematicItem,
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

    @staticmethod
    def undo_and_check(
        qtbot,
        undo_command: DeleteNodeCommand,
        original_node_config: dict,
        original_edges: list[str | int],
        undo_button: QPushButton,
        redo_button: QPushButton,
        model_config: ModelConfig,
        schematic: Schematic,
    ) -> None:
        """
        Undo the node deletion action and check that the node and its edges are
        properly restored.
        :param qtbot: The qtbot instance.
        :param undo_command: The undo command instance.
        :param original_node_config: The config dictionary of the deleted node.
        :param original_edges: The list of edges of the deleted node.
        :param undo_button: The undo button instance.
        :param redo_button: The redo button instance.
        :param model_config: The ModelConfig instance.
        :param schematic: The schematic instance.
        :return: None
        """
        node_name = original_node_config["name"]
        assert (
            undo_command.deleted_node_configs[0].props == original_node_config
        )
        assert sorted(undo_command.deleted_edges) == sorted(original_edges)

        # undo
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True

        # node is restored
        assert (
            model_config.nodes.get_node_config_from_name(node_name)
            == original_node_config
        )
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

    def test_delete_node(self, qtbot, init_window) -> None:
        """
        Tests that the nodes are properly deleted from the schematic and the model
        configuration.
        """
        node_name = "Link2"
        window, schematic, node_op_panel = init_window
        model_config = schematic.model_config
        original_node_config: dict = (
            model_config.nodes.get_node_config_from_name(node_name)
        )
        original_edges = [
            edge for edge in model_config.edges.get_all() if node_name in edge
        ]

        panel = schematic.app.toolbar.tabs["Nodes"].panels["Undo"]
        undo_button = panel.buttons["Undo"]
        redo_button = panel.buttons["Redo"]

        node = schematic.schematic_items[node_name]
        removed_edges = node.edges
        node.on_delete_node()

        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False
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
        self.undo_and_check(
            qtbot=qtbot,
            undo_command=undo_command,
            original_node_config=original_node_config,
            original_edges=original_edges,
            undo_button=undo_button,
            redo_button=redo_button,
            model_config=model_config,
            schematic=schematic,
        )

        # 3. Rename node to test the new node configuration is used when the node
        # is restored
        new_name = "New node name"
        # mock node renaming in NodeDialogForm
        model_config.nodes.rename(node_name, new_name)
        schematic.reload()
        for oi, or_edge in enumerate(original_edges):
            try:
                i = or_edge.index(node_name)
                original_edges[oi][i] = or_edge[i].replace(node_name, new_name)
            except IndexError:
                continue

        # 4. Test redo operation
        # get new schematic item instance
        node = schematic.schematic_items[new_name]
        removed_edges = node.edges

        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False

        self.is_node_deleted(
            model_config=model_config,
            node_name=new_name,
            schematic=schematic,
            removed_edges=removed_edges,
        )

        # 5. Restore node with new configuration
        assert original_node_config["name"] == new_name
        self.undo_and_check(
            qtbot=qtbot,
            undo_command=undo_command,
            original_node_config=original_node_config,
            original_edges=original_edges,
            undo_button=undo_button,
            redo_button=redo_button,
            model_config=model_config,
            schematic=schematic,
        )

    def test_undo_node_rename(self, qtbot, init_window) -> None:
        """
        Tests that, when a node is deleted and a node that what previously connected
        to it is renamed, the deleted edge is not restored. The deleted edge is not
        valid anymore because the node changed name.
        """
        node_name = "Link2"
        window, schematic, node_op_panel = init_window
        model_config = schematic.model_config
        node_item = schematic.schematic_items[node_name]
        assert len(node_item.edges) == 3

        panel = schematic.app.toolbar.tabs["Nodes"].panels["Undo"]
        undo_button = panel.buttons["Undo"]

        node_item.on_delete_node()

        # rename Link1 and undo
        model_config.nodes.rename("Link1", "New Link1")
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)

        # edge is not in model config
        assert model_config.edges.find_edge("Link1", node_name)[0] is None
        assert model_config.edges.find_edge("New Link1", node_name)[0] is None

        # edge item on schematic is not restored
        node_item = schematic.schematic_items[node_name]
        assert len(node_item.edges) == 2

        assert [n.name for n in node_item.connected_nodes["source_nodes"]] == [
            "Link3",
        ]
        assert [n.name for n in node_item.connected_nodes["target_nodes"]] == [
            "Link4",
        ]

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
            for node_name in sorted(nodes_to_delete)
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
        for ni, node_config in enumerate(undo_command.deleted_node_configs):
            assert (
                node_config.props == original_node_config_dict[node_config.name]
            )
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
