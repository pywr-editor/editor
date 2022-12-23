import os
from pathlib import Path
from typing import TYPE_CHECKING

from pandas import HDFStore
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit

from pywr_editor.form import FormCustomWidget, FormField, FormValidation
from pywr_editor.utils import Logging, get_signal_sender
from pywr_editor.widgets import PushButton

if TYPE_CHECKING:
    from pywr_editor.dialogs import ParameterDialogForm

"""
 This widget loads the content of a H5 file and
 handles slots and signals when the file is changed
"""


class H5FileWidget(FormCustomWidget):
    file_changed = None

    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
    ):
        """
        Initialises the input field to edit the H5 file path.
        :param name: The field name.
        :param value: The table file.
        :param parent: The parent widget.
        """
        self.form: "ParameterDialogForm"
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with {value}")

        super().__init__(name, value, parent)
        self.model_config = self.form.model_config
        self.value, self.warning_message, self.keys = self.sanitise_value(value)

        # field
        self.line_edit = QLineEdit()
        self.line_edit.setText(self.value)
        # noinspection PyTypeChecker
        self.file_changed = self.line_edit.textChanged
        # noinspection PyUnresolvedReferences
        self.file_changed.connect(self.on_update_file)

        # browse button
        self.browse_button = PushButton("Browse...", small=True)
        # noinspection PyUnresolvedReferences
        self.browse_button.clicked.connect(self.on_browse_table_file)

        # reload button
        self.reload_button = PushButton("Reload", small=True)
        self.reload_button.setToolTip(
            "Reload the table file in case its content changed"
        )
        # noinspection PyUnresolvedReferences
        self.reload_button.clicked.connect(self.on_reload_click)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.reload_button)

        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        self.form_field.set_warning_message(self.warning_message)

    def sanitise_value(
        self, value: str | None
    ) -> [str, str | None, dict[str, list[str]]]:
        """
        Sanitises the value.
        :param value: The file path.
        :return: The sanitised value, the error message and the store keys.
        """
        self.logger.debug(f"Sanitising value {value}")
        keys = {}
        message = None

        # check value
        if not value:
            return self.get_default_value(), message, keys
        # value must be a string
        elif not isinstance(value, str):
            message = (
                "The value provided in the model configuration must be a valid "
                + "string"
            )
            return self.get_default_value(), message, keys
        elif not value.endswith(".h5"):
            message = "The file extension must be .h5"
            return value, message, keys

        # if valid string, convert to absolute path
        full_file = self.model_config.normalize_file_path(value)
        self.logger.debug(f"Converting file to absolute path {full_file}")
        if not self.model_config.does_file_exist(full_file):
            message = "The file does not exist"
        else:
            keys = self.load_table_keys(full_file)
            self.logger.debug(f"Keys are {keys}")
            # invalid keys
            if not keys:
                message = "The file does not have valid keys"
            # if the path is absolute convert to relative if possible
            elif value is not None and os.path.isabs(value):
                value = self.model_config.path_to_relative(value, False)
                # file is outside the model configuration folder
                if ".." in value:
                    message = (
                        "It is always recommended to place the table file in the "
                        + "same folder as the model configuration file"
                    )

                self.line_edit.blockSignals(True)
                self.line_edit.setText(value)
                self.line_edit.blockSignals(False)

        return value, message, keys

    def get_default_value(self) -> str:
        """
        The field default value.
        :return: An empty string.
        """
        return ""

    def get_value(self) -> str | None:
        """
        Returns the form field value.
        :return: The form field value, None if no file is set.
        """
        value = self.value
        if value:
            return value
        return None

    def validate(
        self, name: str, label: str, value: str | None
    ) -> FormValidation:
        """
        Checks that the file url is valid and the keys are loaded.
        :param name: The field name.
        :param label: The field label.
        :param value: The field label.
        :return: The FormValidation instance.
        """
        if self.keys:
            self.logger.debug("Validation passed")
            return FormValidation(validation=True)

        self.logger.debug("Validation failed")
        return FormValidation(
            validation=False,
            error_message="You must provide a valid file containing a table",
        )

    # noinspection PyProtectedMember
    @staticmethod
    def load_table_keys(file: str) -> dict:
        """
        Loads the table keys (node and where attributes).
        :param file: The path to the file.
        :return: A dictionary containing for each node the where attributes.
        """
        if not Path(file).exists():
            return {}

        keys_dict = {}
        # noinspection PyBroadException
        try:
            with HDFStore(file) as store:
                for group in store._handle.walk_groups():
                    group_name = group._v_pathname
                    for array in store._handle.list_nodes(
                        group, classname="Array"
                    ):
                        if group_name not in keys_dict:
                            keys_dict[group_name] = [array.name]
                        else:
                            keys_dict[group_name].append(array.name)
        except Exception:
            pass

        return keys_dict

    @Slot()
    def on_update_file(self, file: str) -> None:
        """
        Updates the stored file.
        :param file: The text set in the url field.
        :return: None
        """
        self.logger.debug(
            "Running on_update_file Slot because file changed from "
            + get_signal_sender(self)
        )
        self.form_field.clear_message()
        self.value, self.warning_message, self.keys = self.sanitise_value(file)
        self.form_field.set_warning_message(self.warning_message)

    def reset(self) -> None:
        """
        Resets the widget and message.
        :return: None
        """
        self.form_field.clear_message()
        self.line_edit.setText("")

    @Slot()
    def on_browse_table_file(self) -> None:
        """
        Browse for a file. If a file is selected, this is added to the text field.
        :return: None
        """
        self.logger.debug("Opening file dialog")
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        files_filter = "HDF5 (*.h5)"
        file_dialog.setNameFilter(files_filter)

        file_dialog.exec()
        files = file_dialog.selectedFiles()
        if len(files) > 0:
            value = files[0]
            self.logger.debug(f"Selected {value}")
            self.line_edit.setText(value)

    @Slot()
    def on_reload_click(self) -> None:
        """
        Reloads the data stored in the table.
        :return: None
        """
        self.logger.debug(
            f"Called on_reload_click Slot from {get_signal_sender(self)}"
        )
        # trigger Signal to update keys and notify other widgets that keys have been
        # updated
        # noinspection PyUnresolvedReferences
        self.file_changed.emit(self.value)
