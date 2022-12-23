from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPen, Qt

from pywr_editor.style import Color

from ..circle import Circle

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class Works(Circle):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the class for a works' node.
        :param parent: The parent node
        :return None
        """
        super().__init__(
            parent=parent,
            fill=Color("gray", 900),
            outline=Color("gray", 900),
            label=Color("gray", 700),
        )

        self.size = [22, 22]
        self.radius = self.size[0] / 2

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paints the works.
        :param painter: The painter object.
        :param option: The option.
        :param widget: The widget.
        :return: None
        """
        # background
        fill = self.fill
        if self.hover or self.isSelected():
            fill = self.focus_color

        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(fill.qcolor)
        bbox = self.boundingRect()
        padding = 2
        w = self.outline_width
        rect = QRectF(
            bbox.x() + padding - w,
            bbox.y() + padding - w,
            bbox.width() - padding * 2 + w * 2,
            bbox.height() - padding * 2 + w * 2,
        )
        painter.drawPie(rect, 0, -90 * 16)
        painter.drawPie(rect, -180 * 16, -90 * 16)

        pen = QPen()
        pen.setColor(self.outline.qcolor)
        if self.isSelected():
            pen.setWidth(self.outline_width * 1.5)
        else:
            pen.setWidth(self.outline_width)

        # outer border
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.setPen(pen)
        painter.drawEllipse(QPointF(0, 0), self.radius, self.radius)
