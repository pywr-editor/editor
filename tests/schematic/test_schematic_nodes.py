import pytest
from typing import Tuple
from PySide6.QtCore import Qt, QPoint
from pywr_editor import MainWindow
from pywr_editor.schematic import Schematic, SchematicItem, Edge
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

    def test_delete_node(self, qtbot, init_window) -> None:
        """
        Tests that the nodes are properly deleted from the schematic and the model
        configuration.
        """
        window, schematic, node_op_panel = init_window
        model_config = schematic.model_config

        node = schematic.schematic_items["Link2"]
        removed_edges = node.edges
        # noinspection PyArgumentList
        node.on_delete_node()

        assert model_config.has_changes is True

        # the node is removed from the model configuration
        assert model_config.nodes.find_node_index_by_name("Link2") is None

        # node is removed from the items list
        assert "Link2" not in schematic.schematic_items.keys()

        # node is removed from the schematic as graphical item
        node_names = [
            node.name
            for node in schematic.items()
            if isinstance(node, SchematicItem)
        ]
        assert "Link2" not in node_names

        # the node edges are removed from the model configuration
        assert model_config.edges.get_targets("Link2") is None

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
        assert "Link2" not in all_connected_node_names

    def test_delete_nodes(self, qtbot, init_window) -> None:
        """
        Tests that multiple selected nodes are properly deleted.
        """
        window, schematic, node_op_panel = init_window
        model_config = schematic.model_config
        nodes_to_delete = ["Reservoir", "Link3"]
        deleted_schematic_edges = set()

        # select 3 nodes
        for node in nodes_to_delete:
            schematic_item = schematic.schematic_items[node]
            schematic_item.setSelected(True)
            deleted_schematic_edges = set.union(
                deleted_schematic_edges, schematic_item.edges
            )

        # delete them
        panel = window.toolbar.tabs["Nodes"].panels["Operations"]
        qtbot.mouseClick(panel.buttons["Delete"], Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True

        # deleted nodes are not in the model config anymore
        left_nodes = [
            node_dict["name"] for node_dict in model_config.nodes.get_all()
        ]
        assert set(left_nodes) - set(nodes_to_delete) == set(left_nodes)

        # their edges have been deleted as well
        for edge in model_config.edges.get_all():
            assert edge[0] not in nodes_to_delete
            assert edge[1] not in nodes_to_delete

        # nodes have been deleted from the schematic
        assert set(schematic.schematic_items.keys()) - set(left_nodes) == set()

        # edges deleted from schematic
        all_left_schematic_edges = set()
        for node in schematic.schematic_items.values():
            all_left_schematic_edges = set.union(
                all_left_schematic_edges, node.edges
            )
        for schematic_edge in deleted_schematic_edges:
            assert schematic_edge not in all_left_schematic_edges

        # edges to already existing nodes have been deleted
        assert model_config.edges.get_all() == [["Link1", "Link2"]]

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
            "Link4",
            "Reservoir",
        ]
