from functools import partial
from typing import TYPE_CHECKING, Literal

from PySide6.QtCore import QDate, Qt, Slot
from PySide6.QtWidgets import QGridLayout, QLabel, QSizePolicy, QWidget

from pywr_editor.style import Color
from pywr_editor.widgets import DateEdit, SpinBox

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class TimeStepperWidget(QWidget):
    def __init__(self, parent: "MainWindow"):
        """
        Initialises the widget.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.app = parent
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

        # timestep
        main_layout.addWidget(QLabel("Timestep"), 0, 3)
        time_step = SpinBox()
        time_step.setValue(self.model_config.time_delta)
        time_step.setRange(1, 365)
        time_step.setSuffix(" days")
        time_step.setObjectName("time_step")
        time_step.setStyleSheet(
            "#time_step { padding: 2px; border: 1px solid "
            + Color("gray", 400).hex
            + "}"
        )
        # noinspection PyUnresolvedReferences
        time_step.valueChanged.connect(self.time_step_changed)
        main_layout.addWidget(time_step, 0, 4)

        # run to date
        main_layout.addWidget(QLabel("Run to date"), 1, 3)
        saved_run_to_date = parent.editor_settings.run_to_date
        if saved_run_to_date is None:
            saved_run_to_date = self.model_config.end_date
        run_to_date = DateEdit(saved_run_to_date)
        run_to_date.setObjectName("run_to_date")
        # noinspection PyUnresolvedReferences
        run_to_date.dateChanged.connect(
            lambda date: parent.editor_settings.save_run_to_date(
                date.toString("yyyy-MM-dd")
            )
        )
        main_layout.addWidget(run_to_date, 1, 4)

        # separator
        separator = QWidget()
        separator.setFixedHeight(60)
        separator.setFixedWidth(1)
        separator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        separator.setStyleSheet(f"background-color: {Color('gray', 300).hex}")
        main_layout.addWidget(separator, 0, 2, 0, 1, Qt.AlignmentFlag.AlignHCenter)
        main_layout.setColumnMinimumWidth(2, 15)

        self.setLayout(main_layout)

    @Slot(QDate)
    def date_changed(
        self,
        date_type: Literal["start_date", "end_date"],
        date: QDate,
    ) -> None:
        """
        Updates the timestepper dates in the model when the date field is changed.
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

    @Slot(int)
    def time_step_changed(
        self,
        step: int,
    ) -> None:
        """
        Updates the timestepper timestep in the model when the field is changed.
        :param step: The timestep as number of days.
        :return: None
        """
        self.model_config.time_delta = step
        self.app.components_tree.reload()
