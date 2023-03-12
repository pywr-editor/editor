from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pywr_editor.schematic import (
        AbstractSchematicItem,
        SchematicNode,
        SchematicText,
    )


class SchematicItemUtils:
    def __init__(
        self,
        schematic_size: list[float],
        item: Union["AbstractSchematicItem", "SchematicNode", "SchematicText"],
    ):
        """
        Initialises the class.
        :param schematic_size: The schematic width and height.
        :param item: The schematic item instance.
        """
        self.schematic_size = schematic_size
        self.item = item
        # the node current position
        self.item_position = self.item.scenePos()
        # the node bounding rectangle
        self.item_bbox = self.item.sceneBoundingRect()

    @property
    def is_outside_left_edge(self) -> bool:
        """
        Checks if the item bounding rectangle is outside the left edge of the schematic.
        :return: True if the item is outside, False otherwise.
        """
        return round(self.item_bbox.x(), 5) < 0

    @property
    def is_outside_right_edge(self) -> bool:
        """
        Checks if the item bounding rectangle is outside the right edge of the
        schematic.
        :return: True if the item is outside, False otherwise.
        """
        return round(self.item_bbox.right(), 5) > self.schematic_size[0]

    @property
    def is_outside_top_edge(self) -> bool:
        """
        Checks if the item bounding rectangle is outside the top edge of the schematic.
        :return: True if the item is outside, False otherwise.
        """
        return round(self.item_bbox.y(), 5) < 0

    @property
    def is_outside_bottom_edge(self) -> bool:
        """
        Checks if the item bounding rectangle is outside the top edge of the schematic.
        :return: True if the item is outside, False otherwise.
        """
        return round(self.item_bbox.bottom(), 5) > self.schematic_size[1]

    def move_to_left_edge(self) -> None:
        """
        Moves the item so that it is aligned to the schematic left edge.
        :return: None.
        """
        self.item.setX(self.item_position.x() - self.item_bbox.x())

    def move_to_right_edge(self) -> None:
        """
        Moves the item so that it is aligned to the schematic right edge.
        :return: None.
        """
        self.item.moveBy(-(self.item_bbox.right() - self.schematic_size[0]), 0)

    def move_to_top_edge(self) -> None:
        """
        Moves the item so that it is aligned to the schematic top edge.
        :return: None.
        """
        self.item.setY(self.item_position.y() - self.item_bbox.y())

    def move_to_bottom_edge(self) -> None:
        """
        Moves the item so that it is aligned to the schematic bottom edge.
        :return: None.
        """
        self.item.moveBy(0, -(self.item_bbox.bottom() - self.schematic_size[1]))
