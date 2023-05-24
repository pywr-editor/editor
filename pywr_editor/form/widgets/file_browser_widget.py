from pathlib import Path
from typing import TYPE_CHECKING

import qtawesome as qta
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit

from pywr_editor.form import FormCustomWidget, FormField, Validation
from pywr_editor.utils import Logging, get_signal_sender
from pywr_editor.widgets import PushIconButton

if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentForm

"""
 This widget allows the user to provide the path to a non-existing
 file with a specific extension. This is used, for example, by the
 CSVRecorder to create a new CSV file at the end of the simulation.
"""


class FileBrowserWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
        file_extension: str,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The file path.
        :param parent: The parent widget.
        :param file_extension: The extension of the file.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")
        super().__init__(name, value, parent)

        self.file_extension = file_extension
        self.form: "ModelComponentForm"
        self.model_config = self.form.model_config

        # check the value
        message = None
        if value is not None and not isinstance(value, str):
            message = "The file path must be a valid string"
            value = None
        elif (
            isinstance(value, str)
            and value
            and not value.endswith(f".{file_extension}")
        ):
            message = f"The file extension must be {file_extension.upper()}"

        # line edit
        self.line_edit = QLineEdit()
        self.line_edit.setText(value)
        # noinspection PyUnresolvedReferences
        self.line_edit.editingFinished.connect(self.on_edit_finished)

        # browse button
        self.browse_button = PushIconButton(
            icon=qta.icon("msc.folder-opened"), label="Browse...", small=True
        )
        # noinspection PyUnresolvedReferences
        self.browse_button.clicked.connect(self.on_browse)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_button)

        self.field.set_warning(message)

    @Slot()
    def on_browse(self) -> None:
        """
        Browse for a file. If a file is selected, this is added to the text field.
        :return: None
        """
        self.logger.debug("Opening file dialog")
        model_path = self.model_config.file.file_path
        file_dialog = QFileDialog(
            parent=self,
            caption="Choose a location and file name",
            directory=model_path if model_path else Path().home(),
            filter=f"{self.file_extension.upper()} (*.{self.file_extension})",
        )
        # let user select an existing file or a new one
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        # noinspection PyUnresolvedReferences
        file_dialog.fileSelected.connect(self.on_file_selected)
        file_dialog.exec()

    @Slot()
    def on_edit_finished(self) -> None:
        """
        Slot called when the text input looses its focus.
        :return: None
        """
        self.logger.debug(
            f"Running on_edit_finished Slot from {get_signal_sender(self)}"
        )
        self.on_file_selected(self.line_edit.text())

    @Slot(str)
    def on_file_selected(self, file: str) -> None:
        """
        Slot executed when a new file is selected in the browser dialog
        or the user manually inputs or pastes the path in the text field.
        This updates the line edit and converts the file to a relative
        path only if the file is in the same folder of the JSON model.
        :param file: The path to the file.
        :return: None
        """
        self.logger.debug(
            f"Running on_file_selected Slot from {get_signal_sender(self)}"
        )

        if file:
            self.logger.debug(f"Selected {file}")
            file = self.model_config.path_to_relative(file)

            self.logger.debug(f"Setting {file}")
            self.line_edit.setText(self.model_config.path_to_relative(file))

    def get_value(self) -> str | None:
        """
        Returns the form field value.
        :return: The form field value.
        """
        value = self.line_edit.text()
        if value:
            return value
        return None

    def get_default_value(self) -> str:
        """
        Returns the default value for the widget, when the value is not set.
        :return: The default value.
        """
        return ""

    def validate(self, name: str, label: str, value: str) -> Validation:
        """
        Checks the file extension.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The Validation instance.
        """
        if not value:
            return Validation("You must provide a file path")
        elif value and not value.endswith(self.file_extension):
            return Validation(
                f"The file extension must be {self.file_extension.upper()}",
            )
        return Validation()

    def reset(self) -> None:
        """
        Resets the widget. This empties the file field.
        :return: None
        """
        self.line_edit.setText(self.get_default_value())
