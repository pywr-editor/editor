from math import atan2, cos, pi, sin
from typing import TYPE_CHECKING, Union

import PySide6
from PySide6.QtCore import (
    QLineF,
    QPoint,
    QPointF,
    QRectF,
    QSizeF,
    Qt,
    qFuzzyCompare,
)
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsItem

from pywr_editor.style import Color, ColorName

if TYPE_CHECKING:
    from pywr_editor.schematic import Schematic, SchematicNode


class Edge(QGraphicsItem):
    def __init__(
        self,
        source: Union["SchematicNode", None],
        target: Union["SchematicNode", None],
        edge_color_name: ColorName | None = None,
        hide_arrow: bool = False,
    ):
        """
        Initialises the edge.
        :param source: The source node.
        :param target: The target node.
        :return None.
        """
        super().__init__()
        self.source = source
        self.target = target
        self.source_point: QPointF | None = None
        self.target_point: QPointF | None = None
        self.arrow_size: int = 7
        self.hide_arrow = hide_arrow

        # edge color if available
        self.edge_color = Color("gray", 400).qcolor
        if edge_color_name is not None:
            # noinspection PyBroadException
            try:
                self.edge_color = Color(edge_color_name, 500).qcolor
            except Exception:
                pass

        # ensure that the node is always stacked on top of its edges
        self.setZValue(-1)

        # do not consider edges for mouse inputs
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.source.draw_edge(self)
        self.target.draw_edge(self)
        self.adjust()

    def toggle_arrow(self) -> None:
        """
        Shows or hides the arrow.
        :return: None
        """
        if self.hide_arrow:
            self.hide_arrow = False
        else:
            self.hide_arrow = True
        self.update()

    def adjust(self) -> None:
        """
        Adjusts the source and target points of the edge when one of the node moves.
        :return: None
        """
        if self.source is None or self.target is None:
            return

        line = QLineF(
            self.mapFromItem(self.source, 0, 0),
            self.mapFromItem(self.target, 0, 0),
        )
        length = line.length()
        self.prepareGeometryChange()

        min_distance = min(self.source.node.size) + min(self.target.node.size)
        if length > min_distance:
            edge_offset_source = QPointF(
                (line.dx() * self.source.node.size[0] / 2) / length,
                (line.dy() * self.source.node.size[1] / 2) / length,
            )
            # add padding between the arrow and the target node
            edge_offset_target = QPointF(
                (line.dx() * (self.target.node.size[0] / 2 + 1)) / length,
                (line.dy() * (self.target.node.size[1] / 2 + 1)) / length,
            )

            self.source_point = line.p1() + edge_offset_source
            self.target_point = line.p2() - edge_offset_target
        else:
            self.source_point = self.target_point = line.p1()

    def boundingRect(self) -> PySide6.QtCore.QRectF:
        """
        Defines the edge bounding rectangle.
        :return: The rectangle.
        """
        if self.source is None or self.target is None:
            return QRectF()

        pen_width = 1
        extra = (pen_width + self.arrow_size) / 2

        rect = QRectF(
            self.source_point,
            QSizeF(
                self.target_point.x() - self.source_point.x(),
                self.target_point.y() - self.source_point.y(),
            ),
        )
        return rect.normalized().adjusted(-extra, -extra, extra, extra)

    @staticmethod
    def draw_edge(
        painter: QPainter,
        source_point: QPointF | QPoint,
        target_point: QPointF | QPoint,
        edge_color: QColor,
        arrow_size: int = 7,
        draw_arrow: bool = True,
    ) -> None:
        """
        Draws the edge using the painter instance.
        :param painter: The QPainter instance.
        :param source_point: The source point.
        :param target_point: The target point
        :param edge_color: The color for the edge as QColor instance.
        :param arrow_size: The size of the arrow. Default to 7.
        :param draw_arrow: Whether to draw the arrow. Default to True.
        :return: None
        """
        line = QLineF(source_point, target_point)
        if qFuzzyCompare(line.length(), 0):
            return

        # draw the line
        painter.setPen(
            QPen(edge_color, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        )
        painter.drawLine(line)

        # draw the arrow
        if draw_arrow is False:
            return

        angle = atan2(-line.dy(), line.dx())
        line_centre = line.center()
        target_arrow_p1 = line_centre + QPointF(
            sin(angle - pi / 3) * arrow_size,
            cos(angle - pi / 3) * arrow_size,
        )
        target_arrow_p2 = line_centre + QPointF(
            sin(angle - pi + pi / 3) * arrow_size,
            cos(angle - pi + pi / 3) * arrow_size,
        )

        painter.setBrush(edge_color)
        pol = QPolygonF()
        pol.append(line_centre)
        pol.append(target_arrow_p1)
        pol.append(target_arrow_p2)
        painter.drawPolygon(pol)

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paints the edge.
        :param painter: The painter instance.
        :param option: The style options.
        :param widget: The widget.
        :return: None
        """
        if self.source is None or self.target is None:
            return

        self.draw_edge(
            painter=painter,
            source_point=self.source_point,
            target_point=self.target_point,
            edge_color=self.edge_color,
            arrow_size=self.arrow_size,
            draw_arrow=not self.hide_arrow,
        )


class TempEdge(QGraphicsItem):
    def __init__(self, source: "SchematicNode", view: "Schematic"):
        """
        Initialises the edge.
        :param source: The source node.
        :return None.
        """
        super().__init__()
        self.view = view
        self.source_point: QPointF = source.scenePos()
        self.target_point: QPointF = self.source_point

        # do not consider edges for mouse inputs
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.adjust(self.source_point)

    def adjust(self, target_point: QPointF) -> None:
        """
        Adjusts the target point of the edge and redraws the line.
        :return: None
        """
        self.target_point = target_point
        self.prepareGeometryChange()

    def boundingRect(self) -> QRectF:
        """
        Defines the edge bounding rectangle.
        :return: The rectangle.
        """
        return QRectF(
            0, 0, self.view.schematic_width, self.view.schematic_height
        )

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paints the temporary edge.
        :param painter: The painter instance.
        :param option: The style options.
        :param widget: The widget.
        :return: None
        """
        Edge.draw_edge(
            painter=painter,
            source_point=self.source_point,
            target_point=self.target_point,
            edge_color=Color("gray", 600).qcolor,
        )
