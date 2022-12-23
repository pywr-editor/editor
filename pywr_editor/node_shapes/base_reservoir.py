import math
from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import QPointF, QRect, QRectF
from PySide6.QtGui import QPen, Qt

from pywr_editor.style import Color

from .base_node import BaseNode

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class BaseReservoir(BaseNode):
    # The size in pixel
    size: list[int] = [22, 22]

    def __init__(
        self,
        parent: "SchematicItem",
        fill: Color | None,
        outline: Color,
        label: Color,
    ):
        """
        Initialises the class for a node output.
        :param parent The schematic item.
        :param fill: The fill color.
        :param outline: The outline color.
        :param label: The label_color color.
        """
        super().__init__(parent=parent, fill=fill, outline=outline, label=label)

    @staticmethod
    def draw_reservoir(
        painter: PySide6.QtGui.QPainter,
        pen_width: int,
        bbox: QRect | QRectF,
        size: list[int],
        fill_color: Color,
        outline_color: Color,
        highlight: bool,
        focus_color: Color,
    ) -> None:
        """
        Draws the reservoir.
        :param painter: The painter instance.
        :param pen_width: The pen width.
        :param bbox: The bounding box instance.
        :param size: The shape size.
        :param fill_color: The fill color as Color instance.
        :param outline_color: The outline color as Color instance.
        :param highlight: Whether to highlight the shape.
        :param focus_color: The color as Color instance when highlight is True.
        :return: None
        """
        pen = QPen()
        pen.setWidth(pen_width)

        fill_obj = fill_color
        if highlight:
            fill_obj = focus_color

        pen.setColor(fill_obj.qcolor)
        painter.setPen(pen)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        # draw the waves
        number_of_cycles = 3
        amplitude = 1

        start_point = QPointF(bbox.left() + 2, -2)
        last_point = start_point

        # bbox width is always an int
        points = [x / 10.0 for x in range(0, (int(bbox.width()) - 1) * 10, 5)]
        points_x = []
        points_y = []
        for i in points:
            y = math.cos(number_of_cycles * 2 * math.pi * i / bbox.width())
            next_point = QPointF(
                start_point.x() + i, start_point.y() + y * amplitude
            )
            points_x.append(next_point.x())
            points_y.append(next_point.y())
            painter.drawLine(last_point, next_point)
            last_point = next_point

        # fill empty holes by getting sin crests
        mask = [i for i, p in enumerate(points_y) if p <= min(points_y) + 0.1]
        for pi in mask:
            painter.drawEllipse(points_x[pi] - 2, -2, 5, 2)

        # filling
        rect = QRectF(
            -size[0] / 2,
            -size[1] / 2 - 3,
            bbox.width(),
            size[1] / 2 * 2.3,
        )
        angles = [0 * 16, -180 * 16]
        painter.setBrush(fill_obj.qcolor)
        painter.drawPie(rect, angles[0], angles[1])

        # edge
        pen.setColor(outline_color.qcolor)
        painter.setPen(pen)
        painter.drawArc(rect, angles[0], angles[1])

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paints the reservoir.
        :param painter: The painter object.
        :param option: The option.
        :param widget: The widget.
        :return: None
        """
        self.draw_reservoir(
            painter=painter,
            pen_width=self.outline_width,
            bbox=self.boundingRect(),
            size=self.size,
            fill_color=self.fill,
            outline_color=self.outline,
            highlight=self.hover or self.isSelected(),
            focus_color=self.focus_color,
        )
