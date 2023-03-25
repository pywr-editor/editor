from collections import Counter
from typing import Any

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)

from pywr_editor.form import FormCustomWidget, FormField, FormValidation
from pywr_editor.utils import Logging, get_signal_sender
from pywr_editor.widgets import PushIconButton, TableView

from .metadata_custom_fields_model import MetadataCustomFieldsModel


class MetadataCustomFieldsWidget(FormCustomWidget):
    def __init__(
        self, name: str, value: list[list[str, Any]], parent: FormField
    ):
        """
        Initialises the table view to add, change or delete custom metadata fields.
        :param name: The field name.
        :param value: A list containing a list with the custom field name and value.
        :param parent: The parent widget.
        """
        super().__init__(name=name, value=value, parent=parent)
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with {value}")

        # Initialise the table view
        add_button = PushIconButton(icon=":misc/plus", label="Add", small=True)
        delete_button = PushIconButton(
            icon=":misc/minus", label="Delete", small=True
        )
        self.model = MetadataCustomFieldsModel(fields=value)
        # noinspection PyUnresolvedReferences
        self.model.dataChanged.connect(self.on_value_change)
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.connect(self.on_value_change)
        self.table = TableView(
            model=self.model, toggle_buttons_on_selection=delete_button
        )

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addItem(
            QSpacerItem(10, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        # noinspection PyUnresolvedReferences
        add_button.clicked.connect(self.on_add_new_field)
        delete_button.setDisabled(True)
        # noinspection PyUnresolvedReferences
        delete_button.clicked.connect(self.on_delete_field)

        # description
        label = QLabel()
        label.setText(
            "You can add additional custom fields to the model metadata section. "
            + "Double-click on an item to edit it or click the 'Add; button to "
            + "add more."
        )
        label.setWordWrap(True)

        # widget layout
        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        layout.setContentsMargins(0, 0, 0, 0)

    @Slot()
    def on_add_new_field(self) -> None:
        """
        Adds a new custom field.
        :return: None
        """
        self.logger.debug(
            f"Running on_add_new_field Slot from {get_signal_sender(self)}"
        )
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()

        idx = self.model.rowCount()
        new_value = [f"New field #{idx + 1}", "New value"]
        self.model.fields.append(new_value)
        self.logger.debug(f"Added new field {new_value}")

        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        last_row = self.model.index(idx, 0)
        self.table.edit(last_row)

    @Slot()
    def on_delete_field(self) -> None:
        """
        Deletes selected custom fields.
        :return: None
        """
        self.logger.debug(
            f"Running on_delete_field Slot from {get_signal_sender(self)}"
        )
        indexes = self.table.selectedIndexes()

        # delete by value. Collect only the row values to delete
        row_values = []
        for index in indexes:
            field_value = self.model.fields[index.row()]
            if field_value not in row_values:
                row_values.append(field_value)

        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        for value in row_values:
            self.logger.debug(
                f"Deleted {value[0]}={value[1]} from custom fields"
            )
            self.model.fields.remove(value)

        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        self.table.clear_selection()

    @Slot()
    def on_value_change(self) -> None:
        """
        Enables the form button when the widget is updated.
        :return: None
        """
        self.logger.debug(
            f"Running on_value_change Slot from {get_signal_sender(self)}"
        )
        self.form.save_button.setEnabled(True)

    def validate(self, name: str, label: str, value: Any) -> FormValidation:
        """
        Validates the widget value.
        :param name: The name.
        :param label: The label.
        :param value: The value.
        :return: The FormValidation instance.
        """
        # custom field keys must be unique
        d = Counter([field_data[0] for field_data in self.model.fields])
        duplicated = [k for k, v in d.items() if v > 1]
        if len(duplicated) > 0:
            return FormValidation(
                validation=False,
                error_message="The name of each custom field must be unique, "
                + "but the following names are duplicated: "
                + ", ".join(duplicated),
            )
        return FormValidation(validation=True)

    def get_value(self) -> dict:
        """
        Returns the form field value.
        :return: The form field value as dictionary.
        """
        self.logger.debug(f"Fetching field value {self.value}")
        field_dict = {}
        for field_data in self.model.fields:
            field_dict[field_data[0]] = field_data[1]
        return field_dict
