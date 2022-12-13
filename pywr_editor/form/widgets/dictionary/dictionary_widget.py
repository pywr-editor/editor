from copy import deepcopy
from typing import Any, TYPE_CHECKING
from PySide6.QtCore import Slot, QSize
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QAbstractItemView,
)
from .dictionary_model import DictionaryModel
from pywr_editor.widgets import TableView, PushIconButton
from pywr_editor.utils import get_signal_sender, Logging
from pywr_editor.form import FormField, FormCustomWidget, FormValidation

if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentForm

"""
 Displays a widget to add keys and values for a parameter.
 The widget allows adding a dictionary with the following data type:
    - Boolean
    - Number
    - String
    - Dictionary
    - Nodes
    - Parameters
    - Recorders
    - Tables
    - Numbers
    - 2D array
    - 3D array
    - Scenario
    - Strings
"""


class DictionaryWidget(FormCustomWidget):
    def __init__(
        self, name: str, value: dict[str, Any] | None, parent: FormField
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget {name} with value {value}")

        super().__init__(name=name, value=value, parent=parent)
        self.form: "ModelComponentForm"
        self.model_config = self.form.model_config

        # Check value
        if value is None:
            dictionary = {}
        elif not isinstance(value, dict):
            self.form_field.set_warning_message(
                "The configuration must be a dictionary"
            )
            dictionary = {}
        else:
            dictionary = deepcopy(value)

        # Model
        self.model = DictionaryModel(
            dictionary=dictionary, model_config=self.model_config
        )
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.connect(self.on_value_change)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.add_button = PushIconButton(
            icon=":misc/plus", label="Add", small=True
        )
        self.add_button.setToolTip("Add a new dictionary item")
        # noinspection PyUnresolvedReferences
        self.add_button.clicked.connect(self.on_add_new_item)

        self.edit_button = PushIconButton(
            icon=":misc/edit",
            label="Edit",
            small=True,
            icon_size=QSize(10, 10),
        )
        self.edit_button.setEnabled(False)
        # noinspection PyUnresolvedReferences
        self.edit_button.clicked.connect(self.on_edit_item)
        self.edit_button.setToolTip("Edit the dictionary item")

        self.delete_button = PushIconButton(
            icon=":misc/minus", label="Delete", small=True
        )
        self.delete_button.setToolTip("Delete the selected dictionary item")
        self.delete_button.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.delete_button.clicked.connect(self.on_delete_item)

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.edit_button)
        self.button_layout.addWidget(self.delete_button)

        # Table
        self.table = TableView(
            model=self.model,
            toggle_buttons_on_selection=[self.delete_button, self.edit_button],
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setColumnWidth(0, 200)
        # noinspection PyUnresolvedReferences
        self.table.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )

        # Set layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)
        layout.addLayout(self.button_layout)

    @Slot()
    def on_value_change(self) -> None:
        """
        Enables the form button when the widget is updated.
        :return: None
        """
        self.form.save_button.setEnabled(True)

    @Slot()
    def on_selection_changed(self) -> None:
        """
        Enable or disable the delete button based on the number of selected items.
        :return: None
        """
        self.logger.debug(
            f"Running on_selection_changed Slot from {get_signal_sender(self)}"
        )
        selection = self.table.selectionModel().selection()

        # enable edit button only when item is selected
        self.edit_button.setEnabled(selection.count() == 1)

    def get_value(self) -> dict:
        """
        Returns the dictionary.
        :return: The dictionary.
        """
        return self.model.dictionary

    def get_default_value(self) -> dict:
        """
        The field default value.
        :return: An empty dictionary.
        """
        return {}

    def reset(self) -> None:
        """
        Resets the widget. This empties the table.
        :return: None
        """
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.dictionary = self.get_default_value()
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    @Slot()
    def on_add_new_item(self) -> None:
        """
        Opens the dialog to add a new dictionary item to the table.
        :return: None
        """
        from .dictionary_item_dialog_widget import DictionaryItemDialogWidget

        self.logger.debug(
            f"Running on_add_new_item Slot from {get_signal_sender(self)}"
        )
        dialog = DictionaryItemDialogWidget(
            model_config=self.model_config,
            after_form_save=self.on_form_save,
            parent=self.form.parent,
        )
        dialog.open()

    @Slot()
    def on_edit_item(self) -> None:
        """
        Opens the dialog to edit a dictionary item.
        :return: None
        """
        from pywr_editor.form import DictionaryItemDialogWidget

        self.logger.debug(
            f"Running on_edit_item Slot from {get_signal_sender(self)}"
        )
        current_index = (
            self.table.selectionModel().selection().indexes()[0].row()
        )

        dialog = DictionaryItemDialogWidget(
            model_config=self.model_config,
            dict_key=list(self.model.dictionary.keys())[current_index],
            dict_value=list(self.model.dictionary.values())[current_index],
            after_form_save=self.on_form_save,
            additional_data={
                "index": current_index,
            },
            parent=self.form.parent,
        )
        dialog.open()

    @Slot()
    def on_delete_item(self) -> None:
        """
        Deletes selected dictionary items.
        :return: None
        """
        self.logger.debug(
            f"Running on_delete_row Slot from {get_signal_sender(self)}"
        )
        indexes = self.table.selectedIndexes()
        row_indexes = [index.row() for index in indexes]
        keys = list(self.model.dictionary.keys())
        keys_to_delete = [keys[i] for i in row_indexes]

        # collect items to preserve
        new_dict = {}
        for key, value in self.model.dictionary.items():
            if key not in keys_to_delete:
                new_dict[key] = value

        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.dictionary = new_dict
        self.logger.debug(f"Updated model dictionary to {new_dict}")
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    def on_form_save(
        self, form_data: dict[str, Any], data: dict[str, Any]
    ) -> None:
        """
        Updates the dictionary key/value.
        :param form_data: The form data from DictionaryItemDialogWidget.
        :param data: Any additional data. None for this widget.
        :return: None
        """
        self.logger.debug(
            f"Running post-saving action on_form_save with value {form_data}"
        )
        existing_keys = list(self.model.dictionary.keys())
        key = form_data["key"]

        # an existing item field was edited, check that the key has not changed
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        if data and "index" in data:
            current_key = existing_keys[data["index"]]
            if key != current_key:
                self.logger.debug(
                    f"Renamed key from '{current_key}' to '{key}'"
                )
                del self.model.dictionary[current_key]

        # get the new item value from the data type
        data_type = form_data["data_type"]
        self.model.dictionary[key] = form_data[f"field_{data_type}"]
        self.logger.debug(f"Set value {self.model.dictionary[key]} for '{key}'")
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    def validate(
        self,
        name: str,
        label: str,
        value: dict[str, Any],
    ) -> FormValidation:
        """
        Checks that valid data points are provided.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value. Not used.
        :return: The FormValidation instance.
        """
        self.logger.debug("Validating field")

        if not self.get_value():
            return FormValidation(
                validation=False,
                error_message="You must provide the dictionary configuration",
            )

        return FormValidation(validation=True)
