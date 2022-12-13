import PySide6
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .json_editor import JsonEditor


class LineNumberArea(QWidget):
    def __init__(self, editor: "JsonEditor"):
        """
        Initialises the line number area.
        :param editor: The text editor instance.
        """
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> PySide6.QtCore.QSize:
        """
        Sets the size hint.
        :return: The size.
        """
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event: PySide6.QtGui.QPaintEvent) -> None:
        """
        Paints the area.
        :param event: The event being triggered.
        :return: None
        """
        super().paintEvent(event)
        self.editor.line_number_area_paint_event(event)
