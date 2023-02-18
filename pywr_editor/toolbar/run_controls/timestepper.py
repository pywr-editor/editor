from functools import partial
from typing import TYPE_CHECKING, Literal

from PySide6.QtCore import QDate, Slot
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from pywr_editor.widgets import DateEdit

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class TimeStepperWidget(QWidget):
    def __init__(self, parent: "MainWindow"):
        """
        Initialises the widget.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.model_config = parent.model_config

        main_layout = QGridLayout()
        main_layout.setRowMinimumHeight(0, 40)

        # start date
        main_layout.addWidget(QLabel("Start date"), 0, 0)
        start_date = DateEdit(self.model_config.start_date)
        start_date.setObjectName("start_date")
        # noinspection PyUnresolvedReferences
        start_date.dateChanged.connect(partial(self.date_changed, "start_date"))
        main_layout.addWidget(start_date, 0, 1)

        # end date
        main_layout.addWidget(QLabel("End date"), 1, 0)
        end_date = DateEdit(self.model_config.end_date)
        end_date.setObjectName("end_date")
        # noinspection PyUnresolvedReferences
        end_date.dateChanged.connect(partial(self.date_changed, "end_date"))
        main_layout.addWidget(end_date, 1, 1)

        main_layout.addWidget(QLabel("Run to date"), 0, 3)
        run_to_date = DateEdit(parent.editor_settings.run_to_date)
        # noinspection PyUnresolvedReferences
        run_to_date.dateChanged.connect(
            lambda date: parent.editor_settings.save_run_to_date(
                date.toString("yyyy-MM-dd")
            )
        )
        # save_run_to_date
        main_layout.addWidget(run_to_date, 0, 4)

        self.setLayout(main_layout)

    @Slot(QDate)
    def date_changed(
        self,
        date_type: Literal["start_date", "end_date"],
        date: QDate,
    ) -> None:
        """
        Updates the timestepper dates in the model when the date field
        is changed.
        :param date_type: The changed date ("start_date" or "end_date").
        :param date: The new date.
        :return: None
        """
        date_str = date.toString("yyyy-MM-dd")
        if date_type == "start_date":
            self.model_config.start_date = date_str
        elif date_type == "end_date":
            self.model_config.end_date = date_str
        else:
            raise ValueError("date_type can only be 'start_date' or 'end_date'")
