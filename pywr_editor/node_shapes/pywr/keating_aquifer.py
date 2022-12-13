import PySide6
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPen
from ..base_node import BaseNode
from .pywr_node import PywrNode
from pywr_editor.style import Color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class KeatingAquifer(BaseNode, PywrNode):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises a KeatingAquifer node.
        :param parent: The schematic item group.
        """
        self.label = Color("pink", 700)
        super().__init__(parent=parent, label=self.label)

        self.fill = Color("pink", 200)
        self.outline = Color("pink", 500)
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
        l1 = -(self.radius - self.outline_width)
        l2 = self.radius - self.outline_width
        painter.drawLine(QPointF(l1, 0), QPointF(l2, 0))
        painter.drawLine(QPointF(0, l1), QPointF(0, l2))
