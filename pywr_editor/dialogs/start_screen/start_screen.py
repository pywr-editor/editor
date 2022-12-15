import PySide6
from PySide6.QtCore import Qt, QPoint, QPointF
from PySide6.QtWidgets import QDialog, QHBoxLayout, QWidget
from .left_widget import StartScreenLeftWidget
from .right_widget import StartScreenRightWidget
from pywr_editor.style import Color, stylesheet_dict_to_str, AppStylesheet


class StartScreen(QDialog):
    def __init__(self, parent: QWidget = None):
        """
        Initialises the dialog window.
        :param parent: The parent widget.
        """
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(StartScreenLeftWidget(self))
        layout.addWidget(StartScreenRightWidget(self))

        self.setLayout(layout)
        self.setMinimumSize(700, 400)
        self.setMaximumSize(700, 400)
        self.setStyleSheet(self.stylesheet)

        # remove the window title
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.old_pos: QPoint | QPointF | None = None

    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        """
        Saves the window position.
        :param event: The event being triggered.
        :return: None
        """
        self.old_pos = event.position().toPoint()

    def mouseMoveEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        """
        Moves the window.
        :param event: The event being triggered.
        :return: None
        """
        diff = event.position().toPoint() - self.old_pos
        new_pos = self.pos() + diff
        self.move(new_pos)

    @property
    def stylesheet(self) -> str:
        """
        Defines the widget stylesheet.
        :return: The stylesheet as string.
        """
        style = {
            "QDialog": {
                "background-color": Color("gray", 200).hex,
                "border": f'1px solid {Color("gray", 300).hex}',
            }
        }
        return AppStylesheet().get() + stylesheet_dict_to_str(style)
