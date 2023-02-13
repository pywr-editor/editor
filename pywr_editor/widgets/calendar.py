import PySide6
from PySide6.QtGui import QBrush, QColor, QPen, Qt
from PySide6.QtWidgets import QCalendarWidget, QWidget

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
        format = self.weekdayTextFormat(Qt.DayOfWeek.Saturday)
        format.setForeground(QBrush(Qt.GlobalColor.white))
        # format.setForeground(QBrush(Qt::white, Qt::SolidPattern));
        #
        #    calendarWidget->setWeekdayTextFormat(Qt::Saturday, format);
        self.setStyleSheet(self.stylesheet)

    def paintCell(
        self,
        painter: PySide6.QtGui.QPainter,
        rect: PySide6.QtCore.QRect,
        date: PySide6.QtCore.QDate,
    ) -> None:
        """
        Paints the cell with the date.
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
            painter.drawText(
                rect, Qt.AlignmentFlag.AlignCenter, str(date.day())
            )
            painter.restore()
        else:
            super(CalendarWidget, self).paintCell(painter, rect, date)

    @property
    def stylesheet(self) -> str:
        """
        Returns the style.
        :return: The stylesheet as string.
        """
        header_color = Color("neutral", 600).hex
        return stylesheet_dict_to_str(
            {
                "CalendarWidget": {
                    "border-radius": "5px",
                    "border": f"1px solid {Color('neutral', 400).hex}",
                    "QToolButton": {
                        "background-color": header_color,
                    },
                    "QWidget#qt_calendar_navigationbar": {
                        "background": header_color
                    },
                    # row with days
                    "QWidget": {
                        "alternate-background-color": Color("neutral", 200).hex,
                    },
                    # icons
                    "QWidget#qt_calendar_prevmonth": {
                        "qproperty-icon": "url(:form/caret-left)",
                    },
                    "QWidget#qt_calendar_nextmonth": {
                        "qproperty-icon": "url(:form/caret-right)",
                    },
                    "QSpinBox": AppStylesheet.spin_box(),
                    # days
                    "QAbstractItemView": {
                        "background-color": "white",
                        "selection-background-color": Color("blue", 400).hex,
                        "selection-color": "white",
                    },
                }
            }
        )
