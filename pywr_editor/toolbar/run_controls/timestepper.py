from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDateEdit, QGridLayout, QLabel, QWidget

from pywr_editor.widgets import CalendarWidget

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class TimeStepperWidget(QWidget):
    def __init__(self, parent: "MainWindow"):
        """
        Initialises the widget.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        model_config = parent.model_config

        main_layout = QGridLayout()
        main_layout.setRowMinimumHeight(0, 40)

        # TODO changing start/end date changes the timestepper
        # TODO fix style and reduce fontsize?
        # start date
        main_layout.addWidget(QLabel("Start date"), 0, 0)
        start_date = QDateEdit(model_config.start_date)
        start_date.setDisplayFormat("dd/MM/yyyy")
        start_date.setCalendarPopup(True)
        start_date.setCalendarWidget(CalendarWidget())
        main_layout.addWidget(start_date, 0, 1)

        # end date
        main_layout.addWidget(QLabel("End date"), 1, 0)
        end_date = QDateEdit(model_config.end_date)
        end_date.setDisplayFormat("dd/MM/yyyy")
        end_date.setCalendarPopup(True)
        end_date.setCalendarWidget(CalendarWidget())
        main_layout.addWidget(end_date, 1, 1)

        main_layout.addWidget(QLabel("Run to date"), 0, 3)
        run_to_date = QDateEdit(model_config.end_date)
        run_to_date.setDisplayFormat("dd/MM/yyyy")
        run_to_date.setCalendarPopup(True)
        run_to_date.setCalendarWidget(CalendarWidget())
        main_layout.addWidget(run_to_date, 0, 4)

        self.setLayout(main_layout)
