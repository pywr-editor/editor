from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import QPoint, QPointF
from PySide6.QtGui import QPainterPath, QPen

from pywr_editor.style import Color

from .base_node import BaseNode
from .svg_icon import IconProps, SvgIcon

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class Circle(BaseNode):
    def __init__(
        self,
        parent: "SchematicItem",
        fill: Color,
        outline: Color,
        label: Color | None = None,
        icon: IconProps | None = None,
    ):
        """
        Initialises the class for a circle.
        :param parent: The parent node.
        :param parent: The parent node.
        :param fill: The fill color.
        :param outline: The outline color.
        :param label: The label_color color.
        :param icon: The icon properties.
        :return None
        """
        super().__init__(parent=parent, fill=fill, outline=outline, label=label)

        self.size = [22, 22]
        self.radius = self.size[0] / 2
        self.icon: SvgIcon | None = None

        if icon is not None:
            self.icon = SvgIcon(parent=self, icon=icon)
            self.addToGroup(self.icon)

    def shape(self) -> PySide6.QtGui.QPainterPath:
        """
        Reimplements the shape methods otherwise the item’s hit area would be identical
        to its bounding rectangle. The shape excludes the text so that the node can
        only be dragged by dragging its shape.
        :return:The shape path.
        """
        if isinstance(self.x, int):
            center = QPoint(self.x, self.y)
        else:
            # noinspection PyTypeChecker
            center = QPointF(self.x, self.y)
        path = QPainterPath()
        path.addEllipse(center, self.radius * 2, self.radius * 2)
        return path

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paints the circle.
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
        painter.drawEllipse(QPointF(0, 0), self.radius, self.radius)
