import json
from typing import Tuple

import pytest

from pywr_editor import MainWindow
from pywr_editor.schematic import SchematicItemUtils, SchematicNode
from tests.utils import resolve_model_path


def get_all_node_props() -> dict:
    """
    Reads the node properties file.
    :return: The dictionary with the node properties to test.
    """
    with open(resolve_model_path("node_utils_props.json"), "r") as file:
        return json.load(file)


class BaseTestClass:
    model_file = resolve_model_path("model_1.json")

    @pytest.fixture
    def window(self, qtbot) -> MainWindow:
        """
        Creates a new instance for the dummy window.:
        :param qtbot: The QT bot fixture.
        :return The window instance.
        """
        return MainWindow(self.model_file)

    @pytest.fixture
    def add_node(
        self, window: MainWindow, node_props: dict
    ) -> Tuple[SchematicNode, SchematicItemUtils]:
        """
        Adds a node to the schematic.
        :param window: The window instance.
        :param node_props: The proprieties of the new node to add.
        :return: A tuple with the schematic item and the schematic utility instances.
        """
        schematic = window.schematic
        node_obj = SchematicNode(view=schematic, node_props=node_props)
        schematic.scene.addItem(node_obj)

        return node_obj, SchematicItemUtils(
            item=node_obj,
            schematic_size=[
                schematic.schematic_width,
                schematic.schematic_height,
            ],
        )


class TestNodesOutsideCanvas(BaseTestClass):
    @pytest.mark.parametrize("node_props", [get_all_node_props()["node_inside"]])
    def test_node_inside(self, qtbot, window, add_node, node_props):
        """
        Tests the SchematicItemUtils when a node is inside the schematic canvas.
        """
        node_obj, node_utils_obj = add_node
        assert (
            node_utils_obj.is_outside_top_edge
            and node_utils_obj.is_outside_right_edge
            and node_utils_obj.is_outside_bottom_edge
            and node_utils_obj.is_outside_left_edge
        ) is False

    @pytest.mark.parametrize(
        "node_props", [get_all_node_props()["node_outside_left_edge"]]
    )
    def test_node_outside_left_edge(self, qtbot, window, add_node, node_props):
        """
        Tests the SchematicItemUtils when a node is inside the schematic canvas.
        """
        node_obj, node_utils_obj = add_node
        assert (
            node_utils_obj.is_outside_left_edge is True
            and (
                node_utils_obj.is_outside_right_edge
                and node_utils_obj.is_outside_bottom_edge
                and node_utils_obj.is_outside_top_edge
            )
            is False
        )

    @pytest.mark.parametrize(
        "node_props", [get_all_node_props()["node_outside_top_edge"]]
    )
    def test_node_outside_top_edge(self, qtbot, window, add_node, node_props):
        """
        Tests the SchematicItemUtils when a node is inside the schematic canvas.
        """
        node_obj, node_utils_obj = add_node
        assert (
            node_utils_obj.is_outside_top_edge is True
            and (
                node_utils_obj.is_outside_right_edge
                and node_utils_obj.is_outside_bottom_edge
                and node_utils_obj.is_outside_left_edge
            )
            is False
        )

    @pytest.mark.parametrize(
        "node_props", [get_all_node_props()["node_outside_right_edge"]]
    )
    def test_node_outside_right_edge(self, qtbot, window, add_node, node_props):
        """
        Tests the SchematicItemUtils when a node is inside the schematic canvas.
        """
        node_obj, node_utils_obj = add_node
        assert (
            node_utils_obj.is_outside_right_edge is True
            and (
                node_utils_obj.is_outside_top_edge
                and node_utils_obj.is_outside_bottom_edge
                and node_utils_obj.is_outside_left_edge
            )
            is False
        )

    @pytest.mark.parametrize(
        "node_props", [get_all_node_props()["node_outside_bottom_edge"]]
    )
    def test_node_outside_bottom_edge(self, qtbot, window, add_node, node_props):
        """
        Tests the SchematicItemUtils when a node is inside the schematic canvas.
        """
        node_obj, node_utils_obj = add_node
        assert (
            node_utils_obj.is_outside_bottom_edge is True
            and (
                node_utils_obj.is_outside_top_edge
                and node_utils_obj.is_outside_bottom_edge
                and node_utils_obj.is_outside_left_edge
            )
            is False
        )


class TestMoveNodesToCanvasEdge(BaseTestClass):
    @pytest.mark.parametrize(
        "node_props", [get_all_node_props()["node_outside_left_edge"]]
    )
    def test_node_to_left_edge(self, qtbot, window, add_node, node_props):
        """
        Tests the node is properly moved with the left side of the bbox overlapping
        the canvas left edge.
        """
        node_obj, node_utils_obj = add_node
        node_utils_obj.move_to_left_edge()

        # reload utility
        node_utils_obj = SchematicItemUtils(
            item=node_obj,
            schematic_size=[
                node_utils_obj.schematic_size[0],
                node_utils_obj.schematic_size[1],
            ],
        )

        assert (
            node_obj.sceneBoundingRect().x() == 0
            and node_utils_obj.is_outside_left_edge is False
        )

    @pytest.mark.parametrize(
        "node_props", [get_all_node_props()["node_outside_top_edge"]]
    )
    def test_node_to_top_edge(self, qtbot, window, add_node, node_props):
        """
        Tests the node is properly moved with the top side of the bbox overlapping the
        canvas top edge.
        """
        node_obj, node_utils_obj = add_node
        node_utils_obj.move_to_top_edge()

        # reload utility
        node_utils_obj = SchematicItemUtils(
            item=node_obj,
            schematic_size=[
                node_utils_obj.schematic_size[0],
                node_utils_obj.schematic_size[1],
            ],
        )

        assert (
            node_obj.sceneBoundingRect().y() == 0
            and node_utils_obj.is_outside_top_edge is False
        )

    @pytest.mark.parametrize(
        "node_props", [get_all_node_props()["node_outside_right_edge"]]
    )
    def test_node_to_right_edge(self, qtbot, window, add_node, node_props):
        """
        Tests the node is properly moved with the right side of the bbox overlapping
        the canvas right edge.
        """
        node_obj, node_utils_obj = add_node
        node_utils_obj.move_to_right_edge()

        # reload utility
        node_utils_obj = SchematicItemUtils(
            item=node_obj,
            schematic_size=[
                node_utils_obj.schematic_size[0],
                node_utils_obj.schematic_size[1],
            ],
        )
        assert (
            node_obj.sceneBoundingRect().right()
            == float(node_utils_obj.schematic_size[0])
            and node_utils_obj.is_outside_right_edge is False
        )

    @pytest.mark.parametrize(
        "node_props", [get_all_node_props()["node_outside_bottom_edge"]]
    )
    def test_node_to_bottom_edge(self, qtbot, window, add_node, node_props):
        """
        Tests the node is properly moved with the bottom side of the bbox overlapping
        the canvas bottom edge.
        """
        node_obj, node_utils_obj = add_node
        node_utils_obj.move_to_bottom_edge()

        # reload utility
        node_utils_obj = SchematicItemUtils(
            item=node_obj,
            schematic_size=[
                node_utils_obj.schematic_size[0],
                node_utils_obj.schematic_size[1],
            ],
        )
        assert (
            node_obj.sceneBoundingRect().bottom() == node_utils_obj.schematic_size[1]
            and node_utils_obj.is_outside_bottom_edge is False
        )
