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
    qRgba,
)

from pywr_editor.style import Color


class ExtensionIcon(QIconEngine):
    def __init__(self, file_ext: str | None):
        """
        Initialises the class.
        :param file_ext: The file extension.
        """
        super().__init__()

        self.label = file_ext.replace(".", "")[0:3]

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
        pen = QPen()
        pen.setWidthF(0.7)
        pen.setColor(Color("neutral", 700).qcolor)
        painter.setPen(pen)
        painter.setRenderHints(
            QPainter.Antialiasing
            | QPainter.SmoothPixmapTransform
            | QPainter.TextAntialiasing
        )
        # not from QPixmap
        if rect.x() != 0:
            painter.drawRoundedRect(rect, 4, 4)
            font_size = 10
        else:
            font_size = 15

        # text
        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        font.setPixelSize(font_size)
        color = Color("neutral", 700).qcolor
        painter.setPen(color)
        painter.setFont(font)
        painter.drawText(
            rect,
            self.label,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignCenter,
        )
