from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import Slot
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QGraphicsItem, QStyle

from pywr_editor.style import Color

from .item_utils import SchematicItemUtils

if TYPE_CHECKING:
    from pywr_editor.schematic import Schematic


class AbstractSchematicItem:
    """
    Abstract class holding basic properties and methods of a schematic item.
    """

    def __init__(self, view: "Schematic"):
        """
        Initialise the abstract class.
        :param view: The view where to draw the item.
        """
        self.view = view
        self.prev_position = None

        if not issubclass(type(self).__base__, QGraphicsItem):
            raise TypeError("The class must inherit from QGraphicsItem")

    def adjust_position(self) -> bool:
        """
        Checks that the item bounding box is always within the canvas edges. If it is
        not, then the item is re-positioned on the schematic edge.
        :return: True if the item position is adjusted, False otherwise.
        """
        # prevent the items from being moved outside the schematic edges.
        item_utils = SchematicItemUtils(
            item=self,
            schematic_size=[
                self.view.schematic_width,
                self.view.schematic_height,
            ],
        )

        was_item_moved = False
        if item_utils.is_outside_left_edge:
            item_utils.move_to_left_edge()
            was_item_moved = True
        elif item_utils.is_outside_right_edge:
            item_utils.move_to_right_edge()
            was_item_moved = True
        if item_utils.is_outside_top_edge:
            item_utils.move_to_top_edge()
            was_item_moved = True
        elif item_utils.is_outside_bottom_edge:
            item_utils.move_to_bottom_edge()
            was_item_moved = True

        return was_item_moved

    def save_position_if_moved(self) -> None:
        """
        Save the new item position in the model configuration and update
        self.prev_position.
        :return: None
        """
        raise NotImplementedError(
            "The save_position_if_moved method is not implemented"
        )

    def has_position_changed(self) -> bool:
        """
        Checks if the shape has been moved.
        :return: True if the shape was moved, False otherwise.
        """
        return self.position != self.prev_position

    @property
    def position(self) -> [float, float]:
        """
        Returns the current item's position.
        :return: The position as tuple of floats.
        """
        self: "QGraphicsItem"
        return round(self.scenePos().x(), 5), round(self.scenePos().y(), 5)

    @Slot()
    def on_delete_item(self) -> None:
        """
        Delete the schematic item.
        :return: None
        """
        self.view.on_delete_item([self])

    def draw_outline(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
    ):
        """
        Draws the schematic item outline.
        :return:
        """
        pen = QPen()
        pen.setColor(Color("red", 500).qcolor)
        painter.setPen(pen)

        # avoid flickering by increasing the bbox size by the rectangle outline
        # width
        line_width = pen.width()

        if isinstance(self, QGraphicsItem):
            rect = self.boundingRect()
            rect.setX(rect.x() + line_width)
            rect.setY(rect.y() + line_width)
            rect.setWidth(rect.width() - line_width)
            rect.setHeight(rect.height() - line_width)
            painter.drawRoundedRect(rect, 10, 10)
            # remove default outline
            option.state = QStyle.StateFlag.State_None
