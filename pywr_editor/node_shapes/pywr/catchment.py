from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPainterPath, QPen, Qt

from pywr_editor.style import Color

from ..base_node import BaseNode
from ..svg_icon import IconProps, SvgIcon
from .pywr_node import PywrNode

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class Catchment(BaseNode, PywrNode):
    # The size in pixel. Keep same size as Circle to ensure bbox consistency
    # with other nodes. The shape is scaled below by 20%.
    size: list[int] = [22, 22]

    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the class for a node output.
        :param parent The schematic item.
        """
        super().__init__(
            parent=parent,
            fill=Color("lime", 200),
            outline=Color("lime", 600),
            label=Color("lime", 600),
        )

        self.icon = SvgIcon(
            parent=self,
            icon=IconProps(
                name=":schematic/input",
                fill=Color("lime", 700),
                outline=Color("gray", 50),
                rect=QRectF(-6, -8, 12, 14),
            ),
        )
        self.addToGroup(self.icon)

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paints the catchment.
        :param painter: The painter object.
        :param option: The option.
        :param widget: The widget.
        :return: None
        """
        fill = self.fill
        if self.hover or self.isSelected():
            fill = self.focus_color

        start_angle = -20 * 16
        span_angle = int((180 - start_angle / 16 * 2) * 16)
        arc_rect = QRectF(-11, -14, 22, 22)
        triangle = [QPointF(-10, 1), QPointF(0, 17), QPointF(10, 1)]

        # background
        painter.setBrush(fill.qcolor)
        painter.scale(0.8, 0.8)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPie(arc_rect, start_angle, span_angle)
        painter.drawConvexPolygon(triangle)
        # cover missing pie background
        painter.drawConvexPolygon(
            [QPointF(-11, 2), QPointF(0, -6), QPointF(11, 2)]
        )

        # outline
        pen = QPen()
        pen.setWidth(self.outline_width)
        pen.setColor(self.outline.qcolor)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        painter.drawArc(arc_rect, start_angle, span_angle)

        path = QPainterPath()
        path.moveTo(triangle[0])
        path.lineTo(triangle[1])
        painter.drawPath(path)

        path = QPainterPath()
        path.moveTo(triangle[2])
        path.lineTo(triangle[1])
        painter.drawPath(path)
