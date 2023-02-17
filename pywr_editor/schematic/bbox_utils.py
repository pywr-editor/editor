from dataclasses import dataclass

import PySide6

from .node import SchematicNode
from .shapes.abstract_schematic_shape import AbstractSchematicItem


@dataclass
class ItemInfo:
    item: SchematicNode | AbstractSchematicItem
    """ The item instance """
    value: float
    """ The item information value """


@dataclass
class BoxBoundaries:
    max_x: ItemInfo
    """ The item information for the max x """
    max_y: ItemInfo
    """ The item information for the max y """
    min_x: ItemInfo
    """ The item information for the min x """
    min_y: ItemInfo
    """ The item information for the min y """


@dataclass
class SchematicBBoxUtils:
    items: list[PySide6.QtWidgets.QGraphicsItem] | list[
        SchematicNode | AbstractSchematicItem
    ]

    @property
    def min_max_bounding_box_coordinates(self) -> BoxBoundaries:
        """
        Returns the minimum and maximum x and y coordinates among all schematic item's
        bounding boxes. The built-in method self.scene.itemsBoundingRect() cannot be
        used, as this includes the canvas as well.
        :return: The BoxBoundaries instance with the x and y coordinates and the item
        objects.
        """
        max_y = max_x = 0
        min_x = min_y = None
        item_min_x = item_max_x = None
        item_min_y = item_max_y = None
        for item in self.items:
            # ignore children and work on groups only
            if (
                isinstance(item, (SchematicNode, AbstractSchematicItem))
                is False
            ):
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
            max_x=ItemInfo(item=item_max_x, value=max_x),
            max_y=ItemInfo(item=item_max_y, value=max_y),
            min_x=ItemInfo(item=item_min_x, value=min_x),
            min_y=ItemInfo(item=item_min_y, value=min_y),
        )

    def are_items_on_edges(
        self, rectangle_width: float, rectangle_height: float
    ) -> tuple[bool, bool]:
        """
        Checks if one or more items are on the bottom or right edge of a rectangle of
        given width and height.
        :param rectangle_width: The width of the rectangle.
        :param rectangle_height: The height of the rectangle.
        :return: A tuple containing True if at least one items is on the right and
        bottom of the rectangle.
        """
        is_on_bottom_edge = False
        is_on_right_edge = False
        for item in self.items:
            # ignore children and work on groups only
            if (
                isinstance(item, (SchematicNode, AbstractSchematicItem))
                is False
            ):
                continue
            item_rect = item.sceneBoundingRect()
            if item_rect.right() == rectangle_width:
                is_on_right_edge = True

            if item_rect.bottom() == rectangle_height:
                is_on_bottom_edge = True

        return is_on_right_edge, is_on_bottom_edge
