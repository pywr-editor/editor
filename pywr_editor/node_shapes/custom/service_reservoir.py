from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import QRectF
from PySide6.QtGui import QPen

from pywr_editor.style import Color

from ..base_node import BaseNode

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class ServiceReservoir(BaseNode):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the class for a service reservoir node.
        :param parent: The parent node.
        :return None
        """
        self.label = Color("stone", 500)
        super().__init__(parent=parent, label=self.label)

        self.fill = Color("stone", 400)
        self.outline = Color("stone", 500)
        self.size = [18, 18]

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paints the service reservoir.
        :param painter: The painter object.
        :param option: The option.
        :param widget: The widget.
        :return: None
        """
        pen = QPen()
        pen.setColor(self.outline.qcolor)
        pen.setWidth(self.outline_width)

        fill = self.fill
        if self.hover or self.isSelected():
            fill = self.focus_color

        painter.setPen(pen)
        painter.setBrush(fill.qcolor)
        painter.drawRoundedRect(
            QRectF(
                -self.size[0] / 2,
                -self.size[1] / 2,
                self.size[0],
                self.size[1] - 1,
            ),
            1,
            1,
        )
