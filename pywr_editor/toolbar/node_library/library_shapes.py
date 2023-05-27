from math import atan2, cos, pi, sin
from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import QLineF, QPointF
from PySide6.QtGui import QFont, QPen, QPolygonF, Qt
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsRectItem, QGraphicsTextItem

from pywr_editor.style import Color

if TYPE_CHECKING:
    from .library_item import LibraryItem


class BaseShape:
    """
    Abstract class to use to identify the shapes.
    """

    pass


class TextShape(BaseShape, QGraphicsTextItem):
    def __init__(self, parent: "LibraryItem"):
        """
        Initialise the class.
        :param parent: The LibraryNode instance.
        """
        super().__init__(parent)
        self.hover = False

        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        font.setPointSize(20)
        self.setFont(font)

        self.setPlainText("T")
        self.setX(-10)
        self.setY(-18)
        self.setDefaultTextColor(Color("gray", 800).qcolor)

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget,
    ) -> None:
        """
        Paint the object.
        :param painter: The painter instance.
        :param option: The painter options.
        :param widget: The widget.
        :return: None
        """
        self.setDefaultTextColor(Color("gray", 500 if self.hover else 800).qcolor)
        super().paint(painter, option, widget)


class RectangleShape(BaseShape, QGraphicsRectItem):
    def __init__(self, parent: "LibraryItem"):
        """
        Initialise the class.
        :param parent: The LibraryNode instance.
        """
        super().__init__(parent)
        self.hover = False
        self.setRect(-10, -6, 25, 15)

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paint the object.
        :param painter: The painter instance.
        :param option: The painter options.
        :param widget: The widget.
        :return: None
        """
        pen = QPen()
        pen.setWidth(1.5)
        pen.setBrush(Color("gray", 500 if self.hover else 800).qcolor)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)

        super().paint(painter, option, widget)


class ArrowShape(BaseShape, QGraphicsLineItem):
    def __init__(self, parent: "LibraryItem"):
        """
        Initialise the class.
        :param parent: The LibraryNode instance.
        """
        line = QLineF(-6, -6, 10, 10)
        line.setLength(18)
        line.setAngle(-45)
        BaseShape.__init__(parent)
        QGraphicsLineItem.__init__(self, line)
        self.hover = False

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paint the object.
        :param painter: The painter instance.
        :param option: The painter options.
        :param widget: The widget.
        :return: None
        """
        arrow_size = 6
        color = Color("gray", 500 if self.hover else 800).qcolor

        # draw the edge and line
        painter.setPen(
            QPen(
                color,
                1.5,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.drawLine(self.line())

        angle = atan2(-self.line().dy(), self.line().dx())
        target_point = self.line().p2()
        target_arrow_p1 = target_point + QPointF(
            sin(angle - pi / 3) * arrow_size,
            cos(angle - pi / 3) * arrow_size,
        )
        target_arrow_p2 = target_point + QPointF(
            sin(angle - pi + pi / 3) * arrow_size,
            cos(angle - pi + pi / 3) * arrow_size,
        )

        # painter.setBrush(color)
        pol = QPolygonF()
        pol.append(target_point)
        pol.append(target_arrow_p1)
        pol.append(target_arrow_p2)
        painter.drawPolygon(pol)
