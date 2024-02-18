import PySide6
from PySide6.QtCore import QRectF
from PySide6.QtGui import QPen, Qt
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QGraphicsItem

from pywr_editor.style import Color


class SchematicCanvas(QGraphicsItem):
    def __init__(self, width: float, height: float):
        """
        Initialises the schematic canvas. This is a rectangle wrapping all the shapes.
        :param width: The schematic width.
        :param height: THe schematic height.
        :return None
        """
        super().__init__()
        # schematic width
        self.width = width
        # schematic height
        self.height = height
        # drop shadow - this slows down painting when zoomed
        # self.setGraphicsEffect(self.shadow)
        # always draw the schematic as background
        self.setZValue(-1)
        # speed up rendering performance
        self.setCacheMode(QGraphicsItem.ItemCoordinateCache)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def boundingRect(self):
        """
        Set the bounding box for the canvas.
        :return: None
        """
        return QRectF(0, 0, self.width, self.height)

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Draws the canvas as a rectangle wrapping all the shapes.
        :param painter: The painter instance.
        :param option: The option.
        :param widget: The widget.
        :return: None
        """
        painter.setPen(QPen(Color("gray", 400).hex))
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawRoundedRect(self.boundingRect(), 10, 10)

    @property
    def shadow(self) -> QGraphicsDropShadowEffect:
        """
        Returns the shadow effect object.
        :return: The drop shadow effect instance.
        """
        return QGraphicsDropShadowEffect(
            blurRadius=15, xOffset=3, yOffset=3, color=Color("gray", 500).qcolor
        )

    def update_size(self, width: float, height: float) -> None:
        """
        Updates the schematic size.
        :param width: THe schematic width.
        :param height: THe schematic height.
        :return: None
        """
        self.prepareGeometryChange()
        self.width = width
        self.height = height
        self.update()
