import PySide6
from PySide6.QtGui import QBrush, QColor, QPen, Qt, QTextCharFormat
from PySide6.QtWidgets import QCalendarWidget, QMenu, QWidget

from pywr_editor.style import AppStylesheet, Color, stylesheet_dict_to_str

"""
 Provide a widget with a calendar to
 pick a date
"""


class CalendarWidget(QCalendarWidget):
    def __init__(self, parent: QWidget = None):
        """
        Initialises the widget.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )
        self.setHorizontalHeaderFormat(
            QCalendarWidget.HorizontalHeaderFormat.NoHorizontalHeader
        )

        # change style of weekend's days
        w_format = QTextCharFormat()
        w_format.setForeground(
            QBrush(Color("gray", 800).qcolor, Qt.BrushStyle.SolidPattern)
        )
        self.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, w_format)
        self.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, w_format)
        self.setStyleSheet(self.stylesheet)

        # remove shadow from month selector
        # noinspection PyTypeChecker
        month_menu: QMenu = self.findChild(QMenu)
        # noinspection PyUnresolvedReferences
        month_menu.setWindowFlags(month_menu.windowFlags() | Qt.NoDropShadowWindowHint)

    def paintCell(
        self,
        painter: PySide6.QtGui.QPainter,
        rect: PySide6.QtCore.QRect,
        date: PySide6.QtCore.QDate,
    ) -> None:
        """
        Paints the cell with the active date.
        :param painter: The painter instance.
        :param rect: The rectangle for the cell.
        :param date: The date.
        :return: None
        """
        if date == self.selectedDate():
            painter.save()
            painter.fillRect(
                rect,
                QColor("white"),
            )
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(Color("blue", 400).qcolor)
            painter.drawRoundedRect(rect, 5, 5)
            painter.setPen(QPen(QColor("white")))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(date.day()))
            painter.restore()
        else:
            super(CalendarWidget, self).paintCell(painter, rect, date)

    @property
    def stylesheet(self) -> str:
        """
        Returns the style.
        :return: The stylesheet as string.
        """
        header_color = Color("gray", 600).hex
        spin_box = AppStylesheet.spin_box()
        spin_box["padding"] = "2px 6px"

        return stylesheet_dict_to_str(
            {
                "CalendarWidget": {
                    "border-radius": "5px",
                    "border": f"1px solid {Color('gray', 400).hex}",
                    # month selector
                    "QToolButton": {
                        "background-color": header_color,
                        "padding": "2px",
                        "padding-right": "12px",
                        # reset style for month button when pressed
                        ":pressed": {"background": "none", "border": "none"},
                    },
                    "QMenu": AppStylesheet.misc()["QMenu"],
                    "QWidget#qt_calendar_navigationbar": {"background": header_color},
                    "#qt_calendar_yearbutton, #qt_calendar_monthbutton": {
                        "color": Color("gray", 100).hex
                    },
                    "#qt_calendar_yearbutton:hover, #qt_calendar_monthbutton:hover": {
                        "color": Color("gray", 300).hex
                    },
                    # row with days
                    "QWidget": {
                        "alternate-background-color": Color("gray", 200).hex,
                    },
                    # icons
                    "QWidget#qt_calendar_prevmonth": {
                        "qproperty-icon": "url(:form/caret-left)",
                    },
                    "QWidget#qt_calendar_nextmonth": {
                        "qproperty-icon": "url(:form/caret-right)",
                    },
                    "QSpinBox": spin_box,
                    # days
                    "QAbstractItemView": {
                        "background-color": "white",
                        "selection-background-color": Color("blue", 400).hex,
                        "selection-color": "white",
                    },
                }
            }
        )
