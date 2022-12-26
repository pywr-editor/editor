from dataclasses import dataclass

import PySide6

from .node import SchematicNode


@dataclass
class NodeInfo:
    node: SchematicNode
    """ The node instance """
    value: float
    """ The node information value """


@dataclass
class BoxBoundaries:
    max_x: NodeInfo
    """ The node information for the max x """
    max_y: NodeInfo
    """ The node information for the max y """
    min_x: NodeInfo
    """ The node information for the min x """
    min_y: NodeInfo
    """ The node information for the min y """


@dataclass
class SchematicBBoxUtils:
    items: list[PySide6.QtWidgets.QGraphicsItem] | list[SchematicNode]

    @property
    def min_max_bounding_box_coordinates(self) -> BoxBoundaries:
        """
        Returns the minimum and maximum x and y coordinates among all node's bounding
        boxes. The built-in method self.scene.itemsBoundingRect() cannot be used,
        as this includes the canvas as well.
        :return: The BoxBoundaries instance with the x and y coordinates and the node
        objects.
        """
        max_y = max_x = 0
        min_x = min_y = None
        item_min_x = item_max_x = None
        item_min_y = item_max_y = None
        for item in self.items:
            # ignore children and work on groups only
            if isinstance(item, SchematicNode) is False:
                continue

            bounding_rect = item.sceneBoundingRect()
            if bounding_rect.bottom() > max_y:
                max_y = bounding_rect.bottom()
                item_max_y = item
            if bounding_rect.right() > max_x:
                max_x = bounding_rect.right()
                item_max_x = item

            if min_x is None or bounding_rect.left() < min_x:
                min_x = bounding_rect.left()
                item_min_x = item
            if min_y is None or bounding_rect.top() < min_y:
                min_y = bounding_rect.top()
                item_min_y = item

        return BoxBoundaries(
            max_x=NodeInfo(node=item_max_x, value=max_x),
            max_y=NodeInfo(node=item_max_y, value=max_y),
            min_x=NodeInfo(node=item_min_x, value=min_x),
            min_y=NodeInfo(node=item_min_y, value=min_y),
        )

    def are_nodes_on_edges(
        self, rectangle_width: float, rectangle_height: float
    ) -> tuple[bool, bool]:
        """
        Checks if one or more nodes are on the bottom or right edge of a rectangle of
        given width and height.
        :param rectangle_width: The width of the rectangle.
        :param rectangle_height: The height of the rectangle.
        :return: A tuple containing True if at least one node is on the right and
        bottom of the rectangle.
        """
        is_on_bottom_edge = False
        is_on_right_edge = False
        for node in self.items:
            # ignore children and work on groups only
            if isinstance(node, SchematicNode) is False:
                continue
            node_rect = node.sceneBoundingRect()
            if node_rect.right() == rectangle_width:
                is_on_right_edge = True

            if node_rect.bottom() == rectangle_height:
                is_on_bottom_edge = True

        return is_on_right_edge, is_on_bottom_edge
