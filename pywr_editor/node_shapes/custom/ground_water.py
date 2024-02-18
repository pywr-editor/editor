from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPen

from pywr_editor.style import Color

from ..base_node import BaseNode

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class GroundWater(BaseNode):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the class for a groundwater node.
        :param parent: The parent node.
        :return None
        """
        self.label = Color("violet", 700)
        super().__init__(parent=parent, label=self.label)

        self.fill = Color("violet", 200)
        self.outline = Color("violet", 500)
        self.size = [22, 22]
        self.radius = self.size[0] / 2

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paints the node.
        :param painter: The painter object.
        :param option: The option.
        :param widget: The widget.
        :return: None
        """
        pen = QPen()
        pen.setColor(self.outline.qcolor)

        if self.isSelected():
            pen.setWidth(self.outline_width * 1.2)
        else:
            pen.setWidth(self.outline_width)

        fill = self.fill
        if self.hover or self.isSelected():
            fill = self.focus_color

        painter.setPen(pen)
        painter.setBrush(fill.qcolor)
        painter.drawEllipse(QPointF(0, 0), self.radius, self.radius)
        l1 = -self.radius
        l2 = self.radius
        painter.drawLine(QPointF(l1, 0), QPointF(l2, 0))
        painter.drawLine(QPointF(0, l1), QPointF(0, l2))
