import PySide6
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFocusEvent
from PySide6.QtWidgets import QComboBox, QWidget
from pywr_editor.ui import Color, stylesheet_dict_to_str


class ComboBox(QComboBox):
    def __init__(self, parent: QWidget = None):
        """
        Initialises the ComboBox widget.
        :param parent: The parent widget.
        """
        super().__init__(parent)

        # remove frame for border-radius
        self.view().window().setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        self.setStyleSheet(self.stylesheet)
        # self.view().window().setAttribute(Qt.WA_TranslucentBackground)
        # prevent mouse wheel from changing value on scroll
        self.setFocusPolicy(Qt.StrongFocus)
        # fix tab focus issue
        self.installEventFilter(self)

    def eventFilter(
        self, watched: PySide6.QtCore.QObject, event: PySide6.QtCore.QEvent
    ) -> bool:
        """
        Filters the events.
        :param watched: The object being clicked.
        :param event: The event being triggered
        :return: True to stop the event, False otherwise.
        """
        # for some reason Qt calls FocusOut with TabFocusReason reason after user clicks
        # on an item, even if Tab is not pressed
        if isinstance(event, QFocusEvent) and event.type() == QEvent.FocusOut:
            self.clearFocus()
            return True
        return False

    @property
    def all_items(self) -> list:
        """
        Returns all the items in the dropdown menu.
        :return: A list of items.
        """
        return [self.itemText(i) for i in range(self.count())]

    def wheelEvent(self, e: PySide6.QtGui.QWheelEvent) -> None:
        """
        Prevents user from changing the ComboBox value when the widget has no focus.
        :param e: The event being triggered.
        :return: None
        """
        if self.hasFocus():
            super().wheelEvent(e)
        else:
            e.ignore()

    @property
    def stylesheet(self) -> str:
        """
        Returns the stylesheet for the widget.
        :return: The stylesheet as string.
        """
        return stylesheet_dict_to_str(
            {
                "QComboBox": {
                    "background": "#FFF",
                    "border": f"1px solid {Color('gray', 300).hex}",
                    "border-radius": "4px",
                    "padding": "5px 6px",
                    ":focus": {
                        "border": f"1px solid {Color('blue', 400).hex}",
                    },
                    ":hover": {
                        "background": Color("neutral", 100).hex,
                    },
                    ":focus:hover": {
                        "background": "#FFF",
                    },
                    "::drop-down": {
                        "subcontrol-origin": "padding",
                        "subcontrol-position": "top right",
                        "width": "10px",
                        "padding": "0px 5px",
                        "image": "url(:form/caret-down)",
                        "border-left": 0,
                        "border-top-right-radius": "6px",
                        "border-bottom-right-radius": "6px",
                    },
                    ":on": {
                        "background": "#FFF",
                        "border": f"1px solid {Color('blue', 400).hex}",
                    },
                    ":disabled": {
                        "background": Color("gray", 100).hex,
                        "border": f"1px solid {Color('gray', 300).hex}",
                    },
                    "::drop-down:disabled": {
                        "border-color": Color("gray", 300).hex,
                        "background": Color("gray", 100).hex,
                    },
                },
                "ComboBox QAbstractItemView": {
                    "background": "#FFF",
                    "border": f"1px solid {Color('gray', 300).hex}",
                    "border-radius": "6px",
                    "outline": 0,
                    "padding": "3px",
                    "::item": {
                        "padding": "2px 4px",
                        "border-radius": "4px",
                        "border": "1px solid transparent",
                    },
                    "::item:selected": {
                        "background": Color("blue", 100).hex,
                        "border": f"1px solid {Color('blue', 300).hex}",
                        "color": Color("gray", 800).hex,
                        "font-weight": "bold",
                    },
                    "::item:hover": {
                        "background": Color("blue", 100).hex,
                        "border": f"1px solid {Color('blue', 300).hex}",
                        "color": Color("gray", 800).hex,
                    },
                },
            }
        )
