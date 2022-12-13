import PySide6
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPen
from ..base_node import BaseNode
from .pywr_node import PywrNode
from pywr_editor.style import Color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class AggregatedNode(BaseNode, PywrNode):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the class for an aggregated node.
        :param parent: The parent node.
        :return None
        """
        super().__init__(parent=parent)

        self.size: list[int, int] = [25, 25]
        self.radius: float = self.size[0] / 2

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        pen = QPen()
        pen.setWidth(1)

        fill_1 = Color("blue", 200)
        fill_2 = Color("slate", 200)
        fill_3 = Color("violet", 200)
        if self.hover or self.isSelected():
            fill_1 = fill_1.change_shade(fill_1.shade + 100)
            fill_2 = fill_2.change_shade(fill_2.shade + 100)
            fill_3 = fill_3.change_shade(fill_3.shade + 100)

        pen.setColor(Color(fill_1.name, 500).qcolor)
        painter.setPen(pen)
        painter.setBrush(fill_1.qcolor)
        painter.drawEllipse(
            QPointF(-5, -5), self.radius / 1.8, self.radius / 1.8
        )

        pen.setColor(Color(fill_2.name, 500).qcolor)
        painter.setPen(pen)
        painter.setBrush(fill_2.qcolor)
        painter.drawEllipse(QPointF(0, 3), self.radius / 3, self.radius / 3)

        pen.setColor(Color(fill_3.name, 500).qcolor)
        painter.setPen(pen)
        painter.setBrush(fill_3.qcolor)
        painter.drawEllipse(
            QPointF(5, -5), self.radius / 2.5, self.radius / 2.5
        )
