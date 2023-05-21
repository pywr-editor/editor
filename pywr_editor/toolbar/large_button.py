from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QWidget

from pywr_editor.style import stylesheet_dict_to_str

from .base_button import ToolbarBaseButton


class ToolbarLargeButton(ToolbarBaseButton):
    def __init__(self, parent: QWidget, action: QAction):
        """
        Initialises a panel big button.
        :param parent: The parent widget.
        :param action: The action to attach to the button.
        """
        super().__init__(parent, action)

        # load the button style
        self.setStyleSheet(self.stylesheet)

        self.setMaximumWidth(80)
        self.setMinimumWidth(50)
        self.setMinimumHeight(75)
        self.setMaximumHeight(83)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(32, 32))

    @property
    def stylesheet(self) -> str:
        """
        Defines the widget stylesheet.
        :return: The stylesheet as string.
        """
        style = self.base_stylesheet
        style["QToolButton"]["margin-left"] = "2px"
        style["QToolButton"]["margin-right"] = "2px"
        style["QToolButton::menu-indicator"]["subcontrol-position"] = "bottom center"

        return stylesheet_dict_to_str(style)
