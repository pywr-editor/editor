from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget

from pywr_editor.style import stylesheet_dict_to_str

from .base_button import ToolbarBaseButton


class ToolbarSmallButton(ToolbarBaseButton):
    def __init__(self, parent: QWidget, action: QAction):
        """
        Initialises a panel small button.
        :param parent: The parent widget.
        :param action: The action to attach to the button.
        """
        super().__init__(parent, action)

        # load the button style
        self.setStyleSheet(self.stylesheet)
        # aspect
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setMinimumHeight(28)
        self.setMaximumHeight(28)
        self.setIconSize(QSize(20, 20))

    @property
    def stylesheet(self) -> str:
        """
        Defines the widget stylesheet.
        :return: The stylesheet as string.
        """
        style = self.base_stylesheet
        style["QToolButton"]["margin-right"] = "2px"
        style["QToolButton"]["margin-bottom"] = "1px"
        style["QToolButton"]["margin-left"] = "2px"

        return stylesheet_dict_to_str(style)
