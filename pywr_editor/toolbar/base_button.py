from PySide6.QtCore import Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolButton, QWidget

from pywr_editor.style import Color
from pywr_editor.widgets import ContextualMenu


class ToolbarBaseButton(QToolButton):
    def __init__(self, parent: QWidget, action: QAction):
        """
        Initialises the panel button.
        :param parent: The parent widget.
        :param action: The action to attach to the button.
        """
        super().__init__(parent)
        self.separator = False
        self.dropdown_menu: ContextualMenu | None = None

        # Whether to add a separator on the left side of the button
        if (
            action.data() is not None
            and "separator" in action.data()
            and action.data()["separator"] is True
        ):
            self.separator = True

        # Add menu
        if (
            action.data() is not None
            and "dropdown" in action.data()
            and action.data()["dropdown"] is True
        ):
            self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            self.dropdown_menu = ContextualMenu()
            self.setMenu(self.dropdown_menu)

        self.action = action
        self.setObjectName(f"toolbar_button_{action.text()}")
        self._update_status()
        self.clicked.connect(self.action.trigger)
        self.action.changed.connect(self._update_status)

    @Slot()
    def _update_status(self) -> None:
        """
        Updates the button status when the action changes.
        :return: None
        """
        # check whether C++ object was deleted
        try:
            self.setText(self.action.text())
            self.setStatusTip(self.action.statusTip())
            self.setToolTip(self.action.toolTip())
            self.setIcon(self.action.icon())
            self.setEnabled(self.action.isEnabled())
            self.setCheckable(self.action.isCheckable())
            self.setChecked(self.action.isChecked())
        except RuntimeError:
            pass

    @property
    def base_stylesheet(self) -> dict:
        """
        Defines the widget stylesheet.
        :return: The stylesheet dictionary.
        """
        style = {
            "QToolButton": {
                "border": "1px solid transparent",
                "border-radius": "4px",
                "color": Color("gray", 700).hex,
                "padding": 0,
                "margin-top": "5px",
                "text-align": "left",
            },
            "QToolButton:hover, QToolButton:pressed": {
                "background-color": Color("blue", 200).hex,
                "border": f'1px solid {Color("blue", 400).hex}',
            },
            "QToolButton:checked": {
                "background-color": Color("blue", 200).hex,
                "border": f'1px solid {Color("blue", 400).hex}',
            },
            "QToolButton:disabled": {
                "color": Color("gray", 400).hex,
            },
            "QToolButton::menu-indicator": {
                "padding-top": "3px",
                "height": "9px",
                "image": "url(:toolbar/arrow-down)",
                "width": "9px",
            },
            "QToolButton::menu-indicator:disabled": {
                "image": "url(:toolbar/arrow-down-disabled)",
            },
        }

        if self.separator:
            style["QToolButton"]["border-right"] = f'1px solid {Color("gray", 300).hex}'

        return style
