from typing import Literal

import PySide6
from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import (
    QFont,
    QIconEngine,
    QImage,
    QPainter,
    QPen,
    QPixmap,
    Qt,
    QTextOption,
    qRgba,
)

from pywr_editor.style import Color, ColorName


class IconWithInitials(QIconEngine):
    def __init__(
        self, initials: str | None, shape: Literal["rectangle", "circle"]
    ):
        """
        Initialises the class.
        :param initials: The initials associated to the icon.
        :param shape: The icon shape.
        """
        super().__init__()

        self.label = initials
        self.shape = shape
        self.color = self.get_color()

    def pixmap(
        self,
        size: PySide6.QtCore.QSize,
        mode: PySide6.QtGui.QIcon.Mode,
        state: PySide6.QtGui.QIcon.State,
    ) -> PySide6.QtGui.QPixmap:
        """
        Renders the icon as pixmap. This is used, for example, in QLineEdit of
        QComboBox.
        :param size: The icon size.
        :param mode: The mode.
        :param state: The icon state.
        :return: The QPixmap instance.
        """
        image = QImage(size, QImage.Format_ARGB32)
        image.fill(qRgba(0, 0, 0, 0))
        pixmap = QPixmap.fromImage(
            image, Qt.ImageConversionFlag.NoFormatConversion
        )
        painter = QPainter(pixmap)
        self.paint(painter, QRect(QPoint(0, 0), size), mode, state)
        return pixmap

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        rect: PySide6.QtCore.QRect,
        mode: PySide6.QtGui.QIcon.Mode,
        state: PySide6.QtGui.QIcon.State,
    ) -> None:
        """
        Paints the icon.
        :param painter: The painter instance.
        :param rect: The rectangle.
        :param mode: The item mode.
        :param state: The item state.
        :return: None
        """
        # background and border
        pen = QPen()
        pen.setWidthF(0.7)
        pen.setColor(Color(self.color, 700).qcolor)
        painter.setPen(pen)
        painter.setBrush(Color(self.color, 100).qcolor)
        painter.setRenderHints(
            QPainter.Antialiasing
            | QPainter.SmoothPixmapTransform
            | QPainter.TextAntialiasing
        )

        if self.shape == "rectangle":
            painter.drawRoundedRect(rect, 4, 4)
        elif self.shape == "circle":
            painter.drawEllipse(rect.center(), 8, 8)
        else:
            raise ValueError("Wrong shape type")

        # text
        font = QFont()
        font.setPixelSize(12)
        color = Color(self.color, 700).qcolor
        text_options = QTextOption()
        text_options.setAlignment(Qt.AlignmentFlag.AlignCenter)

        painter.setPen(QPen(color))
        painter.setBrush(color)
        painter.setFont(font)
        if self.label and isinstance(self.label, str):
            painter.drawText(rect, self.label[0].upper(), text_options)

    def get_color(self) -> ColorName:
        """
        Gets the icon color based on the parameter key. For global or default
        parameters, a default color is used.
        :return: The color name.
        """
        raise NotImplementedError("The method get_color() is not implemented")
