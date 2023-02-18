from typing import Tuple

import PySide6
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit, QWidget

from pywr_editor.style import Color, stylesheet_dict_to_str
from pywr_editor.widgets import CalendarWidget


class DateEdit(QDateEdit):
    def __init__(
        self,
        date: PySide6.QtCore.QDate | Tuple[int, int, int],
        parent: QWidget = None,
    ):
        """
        Initialises the widget.
        :param date: The date to set as QDate instance or tuple with year, month and
        day.
        :param parent: The parent widget. Default to None.
        """
        if isinstance(date, tuple):
            date = QDate(*date)
        if date is None:
            date = QDate()

        super().__init__(date, parent)
        self.setDisplayFormat("dd/MM/yyyy")
        self.setCalendarPopup(True)
        self.setCalendarWidget(CalendarWidget())
        self.setStyleSheet(self.stylesheet)

    @property
    def stylesheet(self) -> str:
        """
        Returns the stylesheet for the widget.
        :return: The stylesheet as string.
        """
        return stylesheet_dict_to_str(
            {
                "DateEdit": {
                    "background": "#FFF",
                    "border": f"1px solid {Color('neutral', 300).hex}",
                    "padding": "2px",
                    "border-radius": "4px",
                    "::drop-down": {
                        "image": "url(:form/caret-down)",
                        "width": "12px",
                        "height": "12px",
                        "right": "3px",
                        "top": "5px",
                    },
                }
            }
        )
