from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class SchematicNodeUtils:
    def __init__(self, schematic_size: list[float], node: "SchematicNode"):
        """
        Initialises the class.
        :param schematic_size: The schematic width and height.
        :param node: The node instance.
        """
        self.schematic_size = schematic_size
        self.node = node
        # the node current position
        self.node_position = self.node.scenePos()
        # the node bounding rectangle
        self.node_bbox = self.node.sceneBoundingRect()

    @property
    def is_outside_left_edge(self) -> bool:
        """
        Checks if the node bounding rectangle is outside the left edge of the schematic.
        :return: True if the node is outside, False otherwise.
        """
        return round(self.node_bbox.x(), 5) < 0

    @property
    def is_outside_right_edge(self) -> bool:
        """
        Checks if the node bounding rectangle is outside the right edge of the
        schematic.
        :return: True if the node is outside, False otherwise.
        """
        return round(self.node_bbox.right(), 5) > self.schematic_size[0]

    @property
    def is_outside_top_edge(self) -> bool:
        """
        Checks if the node bounding rectangle is outside the top edge of the schematic.
        :return: True if the node is outside, False otherwise.
        """
        return round(self.node_bbox.y(), 5) < 0

    @property
    def is_outside_bottom_edge(self) -> bool:
        """
        Checks if the node bounding rectangle is outside the top edge of the schematic.
        :return: True if the node is outside, False otherwise.
        """
        return round(self.node_bbox.bottom(), 5) > self.schematic_size[1]

    def move_to_left_edge(self) -> None:
        """
        Moves the item so that it is aligned to the schematic left edge.
        :return: None.
        """
        self.node.setX(self.node_position.x() - self.node_bbox.x())

    def move_to_right_edge(self) -> None:
        """
        Moves the item so that it is aligned to the schematic right edge.
        :return: None.
        """
        self.node.setX(self.schematic_size[0] - self.node_bbox.width() / 2)

    def move_to_top_edge(self) -> None:
        """
        Moves the item so that it is aligned to the schematic top edge.
        :return: None.
        """
        self.node.setY(self.node_position.y() - self.node_bbox.y())

    def move_to_bottom_edge(self) -> None:
        """
        Moves the item so that it is aligned to the schematic top edge.
        :return: None.
        """
        self.node.moveBy(0, -(self.node_bbox.bottom() - self.schematic_size[1]))
