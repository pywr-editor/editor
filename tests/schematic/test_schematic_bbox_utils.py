import pytest

from pywr_editor.schematic import SchematicBBoxUtils, SchematicNodeUtils
from tests.DummyMainWindow import MainWindow
from tests.utils import resolve_model_path


class TestBboxUtils:
    model_file = resolve_model_path("model_3.json")

    @pytest.fixture
    def window(self, qtbot) -> MainWindow:
        """
        Creates a new instance for the dummy window.:
        :param qtbot: The QT bot fixture.
        :return The window instance.
        """
        return MainWindow(self.model_file)

    def test_min_max_bounding_box_coordinates(self, qtbot, window):
        """
        Tests that the max and min coordinates of the nodes' bounding boxes are correct.
        """
        schematic_items = window.schematic.node_items
        max_min_bbox = SchematicBBoxUtils(
            window.schematic.items()
        ).min_max_bounding_box_coordinates

        assert max_min_bbox.max_x.node == schematic_items["Link1"]
        assert (
            max_min_bbox.max_x.value
            == schematic_items["Link1"].sceneBoundingRect().right()
        )

        assert max_min_bbox.min_x.node == schematic_items["Link2"]
        assert (
            max_min_bbox.min_x.value
            == schematic_items["Link2"].sceneBoundingRect().left()
        )

        assert max_min_bbox.max_y.node == schematic_items["Link3"]
        assert (
            max_min_bbox.max_y.value
            == schematic_items["Link3"].sceneBoundingRect().bottom()
        )

        assert max_min_bbox.min_y.node == schematic_items["Link4"]
        assert (
            max_min_bbox.min_y.value
            == schematic_items["Link4"].sceneBoundingRect().top()
        )

    def test_are_nodes_on_edges(self, qtbot, window):
        """
        Tests the method that checks when a node is on the schematic right or bottom
        edge.
        """
        schematic_items = window.schematic.node_items

        # test node initial position
        node_utils_obj = SchematicNodeUtils(
            node=schematic_items["Link1"],
            schematic_size=[
                window.schematic.schematic_width,
                window.schematic.schematic_height,
            ],
        )
        max_min_bbox = SchematicBBoxUtils(
            window.schematic.items()
        ).are_nodes_on_edges(
            window.schematic.schematic_width, window.schematic.schematic_height
        )
        assert max_min_bbox[0] is False
        assert max_min_bbox[1] is False

        # move node to the bottom edge
        node_utils_obj.move_to_bottom_edge()
        max_min_bbox = SchematicBBoxUtils(
            window.schematic.items()
        ).are_nodes_on_edges(
            window.schematic.schematic_width, window.schematic.schematic_height
        )
        assert max_min_bbox[1] is True

        # move node to the right edge
        node_utils_obj.move_to_right_edge()
        max_min_bbox = SchematicBBoxUtils(
            window.schematic.items()
        ).are_nodes_on_edges(
            window.schematic.schematic_width, window.schematic.schematic_height
        )
        assert max_min_bbox[0] is True
