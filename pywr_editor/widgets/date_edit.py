from typing import Tuple

import PySide6
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QDateEdit, QWidget

from pywr_editor.style import Color, stylesheet_dict_to_str
from pywr_editor.widgets import CalendarWidget


class DateEdit(QDateEdit):
    def __init__(
        self,
        date: PySide6.QtCore.QDate | Tuple[int, int, int] | None,
        parent: QWidget = None,
    ):
        """
        Initialises the widget.
        :param date: The date to set as QDate instance or tuple with year, month and
        day or as string as YYYY-MM-DD.
        :param parent: The parent widget. Default to None.
        """
        # convert string to tuple or None if the date is not valid
        if isinstance(date, str):
            # noinspection PyBroadException
            try:
                year, month, day = date.split("-")
                date = int(year), int(month), int(day)
            except Exception:
                date = None

        if isinstance(date, tuple):
            date = QDate(*date)
        elif date is None:
            date = QDate(2000, 1, 1)

        super().__init__(date, parent)
        self.setDisplayFormat("dd/MM/yyyy")
        self.setCalendarPopup(True)
        self.setCalendarWidget(CalendarWidget())
        self.setStyleSheet(self.stylesheet)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

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
                    "border": f"1px solid {Color('gray', 400).hex}",
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
