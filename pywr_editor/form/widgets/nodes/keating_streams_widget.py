from typing import TypeVar, Any
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from .keating_streams_model import KeatingStreamsModel
from pywr_editor.form import (
    FormCustomWidget,
    FormValidation,
    FormField,
)
from pywr_editor.utils import Logging, get_signal_sender
from pywr_editor.widgets import TableView, PushIconButton

"""
 This widget handles the levels in each Keating stream
 and the transmissivity coefficients.
"""

value_type = TypeVar(
    "value_type", bound=dict[str, list[list[float]] | list[float]]
)


class KeatingStreamsWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: value_type,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: A dictionary with the stream_flow_levels and transmissivity keys.
        :param parent: The parent widget.
        """
        super().__init__(name, value, parent)
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with {value}")

        levels, transmissivity, warning_message = self.sanitise_value(value)

        self.model = KeatingStreamsModel(
            levels=levels, transmissivity=transmissivity
        )
        # noinspection PyUnresolvedReferences
        self.model.dataChanged.connect(self.on_value_change)
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.connect(self.on_value_change)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_stream_button = PushIconButton(
            icon=":misc/plus", label="Add stream", small=True
        )
        self.add_stream_button.setToolTip("Add a new row to the table")
        # noinspection PyUnresolvedReferences
        self.add_stream_button.clicked.connect(self.on_add_new_row)

        self.delete_stream_button = PushIconButton(
            icon=":misc/minus", label="Delete stream", small=True
        )
        self.delete_stream_button.setToolTip(
            "Delete the selected row in the table"
        )
        self.delete_stream_button.setEnabled(False)
        # noinspection PyUnresolvedReferences
        self.delete_stream_button.clicked.connect(self.on_delete_row)

        self.add_level_button = PushIconButton(
            icon=":misc/plus", label="Add level", small=True
        )
        self.add_level_button.setToolTip("Add a new column to the table")
        # noinspection PyUnresolvedReferences
        self.add_level_button.clicked.connect(self.on_add_new_column)

        self.delete_level_button = PushIconButton(
            icon=":misc/minus", label="Delete level", small=True
        )
        self.delete_level_button.setToolTip(
            "Delete the selected column in the table"
        )
        self.delete_level_button.setEnabled(False)
        # noinspection PyUnresolvedReferences
        self.delete_level_button.clicked.connect(self.on_delete_column)

        # Button layout
        button_layout.addWidget(self.add_stream_button)
        button_layout.addWidget(self.delete_stream_button)
        button_layout.addStretch()
        button_layout.addWidget(self.add_level_button)
        button_layout.addWidget(self.delete_level_button)

        # Table
        self.table = TableView(self.model)
        self.table.setMaximumHeight(150)
        self.table.verticalHeader().setVisible(True)
        self.table.setSelectionMode(TableView.SelectionMode.SingleSelection)
        # noinspection PyUnresolvedReferences
        self.table.selectionModel().selectionChanged.connect(
            self.toggle_buttons
        )

        # layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        if warning_message:
            self.logger.debug(warning_message)
            self.form_field.set_warning_message(warning_message)

    @Slot()
    def on_value_change(self) -> None:
        """
        Enables the form button and handle the delete buttons when the widget is
        updated.
        :return: None
        """
        self.form.save_button.setEnabled(True)
        self.toggle_buttons()

    @Slot()
    def on_add_new_row(self) -> None:
        """
        Adds a new row to the table.
        :return: None
        """
        self.logger.debug(
            f"Running on_add_new_row Slot from {get_signal_sender(self)}"
        )
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()

        self.model.levels.append([None] * self.model.columnCount())

        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    @Slot()
    def on_delete_row(self) -> None:
        """
        Deletes the selected row.
        :return: None
        """
        self.logger.debug(
            f"Running on_delete_row Slot from {get_signal_sender(self)}"
        )
        indexes = self.table.selectedIndexes()
        row_index = indexes[0].row()

        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        del self.model.levels[row_index]
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

        # remove all data when all streams are deleted
        if self.model.rowCount() == 0:
            self.model.transmissivity = []

    @Slot()
    def on_add_new_column(self) -> None:
        """
        Adds a new column to the table.
        :return: None
        """
        self.logger.debug(
            f"Running on_add_new_column Slot from {get_signal_sender(self)}"
        )
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()

        for level in self.model.levels:
            level.append(None)
        self.model.transmissivity.append(None)

        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    @Slot()
    def on_delete_column(self) -> None:
        """
        Deletes the selected column.
        :return: None
        """
        self.logger.debug(
            f"Running on_delete_column Slot from {get_signal_sender(self)}"
        )
        indexes = self.table.selectedIndexes()
        column_index = indexes[0].column()
        if self.model.columnCount() == 0:
            return

        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()

        for level in self.model.levels:
            del level[column_index]

        del self.model.transmissivity[column_index]

        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    @Slot()
    def toggle_buttons(self) -> None:
        """
        Enable or disable the delete stream button. The button gets disabled if
        the last row (transmissivity) is selected.
        :return: None
        """
        self.logger.debug(
            f"Running toggle_buttons Slot from {get_signal_sender(self)}"
        )
        selection = self.table.selectionModel().selection()

        if selection.indexes():
            total_rows = self.table.model.rowCount()

            # enable the buttons only when one item is selected
            self.delete_stream_button.setEnabled(
                selection.indexes()[0].row() != total_rows - 1
            )
            self.delete_level_button.setEnabled(True)
        else:
            self.delete_stream_button.setEnabled(False)
            self.delete_level_button.setEnabled(False)

    def sanitise_value(
        self, value: value_type
    ) -> tuple[list[list[float]], list[float], str | None]:
        """
        Sanitises the values.
        :param value: The dictionary with the values for each stream and level.
        :return: The list of levels and transmissivity and the warning message.
        """
        warning_message = None
        final_levels = []
        final_transmissivity = []

        levels = value["stream_flow_levels"]
        transmissivity = value["transmissivity"]

        if not levels or not transmissivity:
            self.logger.debug("One of the value in the dictionary is empty")
        # check types
        elif not isinstance(transmissivity, list) or any(
            [not isinstance(t, (int, float)) for t in transmissivity]
        ):
            warning_message = "The transmissivity must be a list of numbers"
        elif not isinstance(levels, list):
            warning_message = "The levels must be a list of lists"
        elif any(
            [not isinstance(stream_levels, list) for stream_levels in levels]
        ) or any(
            not isinstance(stream_level, (int, float))
            for stream_levels in levels
            for stream_level in stream_levels
        ):
            warning_message = (
                "The levels in each stream must be a list of numbers"
            )
        # each stream must have the same number of levels
        elif len({len(stream_levels) for stream_levels in levels}) != 1:
            warning_message = "Each stream must hve the same number of levels"
        # number of levels per stream must equal the transmissivity size
        elif any(
            [
                len(stream_levels) != len(transmissivity)
                for stream_levels in levels
            ]
        ):
            warning_message = (
                "The number of transmissivity coefficients must match the number "
                + "of levels in each stream"
            )
        else:
            final_levels = levels
            final_transmissivity = transmissivity

        return final_levels, final_transmissivity, warning_message

    def get_value(self) -> value_type:
        """
        Returns the data.
        :return: A dictionary with the levels and transmissivity coefficients.
        """
        return {
            "num_streams": len(self.model.levels),
            "stream_flow_levels": self.model.levels,
            "transmissivity": self.model.transmissivity,
        }

    def validate(self, name: str, label: str, value: None) -> FormValidation:
        """
        Checks that all levels and transmissivity coefficients are provided.
        :param name: The field name.
        :param label: The field label.
        :param value: Not used.
        :return: The validation instance.
        """
        if not self.model.levels or not self.model.levels:
            return FormValidation(
                validation=False,
                error_message="You must provide at least one stream with a valid "
                + "level and transmissivity",
            )
        elif any(
            [
                v is None
                for stream_level in self.model.levels
                for v in stream_level
            ]
        ):
            return FormValidation(
                validation=False,
                error_message="You must provide all the levels for each stream",
            )
        elif any([v is None for v in self.model.transmissivity]):
            return FormValidation(
                validation=False,
                error_message="You must provide all the transmissivity coefficients "
                + "for each level",
            )

        return FormValidation(validation=True)

    def after_validate(
        self, form_dict: dict[str, Any], form_field_name: str
    ) -> None:
        """
        Unpacks the form data.
        :return: None
        """
        for key, value in form_dict[form_field_name].items():
            form_dict[key] = value
        del form_dict[form_field_name]
