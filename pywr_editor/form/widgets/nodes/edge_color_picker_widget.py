from PySide6.QtCore import QPointF
from PySide6.QtGui import QIcon, QPainter, QPixmap, Qt
from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import FormCustomWidget, FormField
from pywr_editor.style import Color
from pywr_editor.utils import Logging
from pywr_editor.widgets import ComboBox


class EdgeColorPickerWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: str,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected colour.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")

        super().__init__(name, value, parent)

        # set default colour if name is not correct
        if not value or value not in Color.colors:
            value = self.get_default_value()

        self.combo_box = ComboBox()
        for key in Color.colors.keys():
            # color name
            color_name = key.title()
            if key == self.get_default_value():
                color_name += " (Default)"

            self.combo_box.addItem(
                QIcon(self.get_pixmap_from_color(key)), color_name, key
            )
        self.combo_box.setCurrentIndex(self.combo_box.findData(value))

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

    @staticmethod
    def get_pixmap_from_color(color_name: str) -> QPixmap:
        """
        Draws a circle with the color_name and return the pixmap object.
        :param color_name: The color name.
        :return: The QPixmap instance.
        """
        size = 16
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter()
        painter.begin(pixmap)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(Color(color_name, 400).qcolor)
        painter.drawEllipse(QPointF(size / 2, size / 2), 7, 7)
        painter.end()

        return pixmap

    def get_default_value(self) -> str:
        """
        The default colour.
        :return: The default colour.
        """
        return "gray"

    def get_value(self) -> str | None:
        """
        Returns the selected colour
        :return: The colour or None if the default colour is selected.
        """
        value = self.combo_box.currentData()
        if value == self.get_default_value():
            return None
        return value
