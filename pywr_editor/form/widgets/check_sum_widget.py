import hashlib
import io
import os
import traceback
from pathlib import Path
from typing import TYPE_CHECKING, Any

import qtawesome as qta
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from pywr_editor.form import (
    AbstractStringComboBoxWidget,
    FormField,
    FormValidation,
)
from pywr_editor.widgets import PushIconButton

if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentForm


"""
 Widget used to show and calculate the checksum of files
 handled by the DataFrameParameter and TablesArrayParameter
 or any other section offering the "url" field.

 Although pywr allows providing more than one checksum, the
 widget only shows and returns the first available checksum
 in the value dictionary.
"""


class CheckSumWidget(AbstractStringComboBoxWidget):
    def __init__(self, name: str, value: dict | None, parent: FormField):
        """
        Initialises the widget.
        :param name: The name,
        :param value: A dictionary with the checksum name and value.
        :param parent: The parent widget.
        """
        # Get algorithms - exclude those not supported by pywr
        algorithms_dict = {
            alg_name: alg_name.replace("_", " ").title()
            for alg_name in hashlib.algorithms_available
            if alg_name not in ["shake_256"]
        }
        labels_map = {**{"None": "None"}, **algorithms_dict}

        # Extract the first algorithm and hash
        selected_algorithm = "None"
        hash = ""
        if isinstance(value, dict) and len(value) > 0:
            selected_algorithm = list(value.keys())[0]
            hash = list(value.values())[0]

        super().__init__(
            name=name,
            value=selected_algorithm,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=labels_map,
            default_value="None",
        )

        self.logger.debug(f"Using algorithm: {selected_algorithm}")
        self.logger.debug(f"Using hash: {hash}")

        # add hash widget
        self.line_edit = QLineEdit()
        self.line_edit.setText(hash)
        self.render_fields()

        # algorithm is provided bust hash is missing
        if selected_algorithm != "None" and not hash:
            message = "You must provide the file hash"
            if self.warning_message is not None:
                self.warning_message += f". {message}"
            else:
                self.warning_message = message

    def render_fields(self) -> None:
        """
        Renders the CheckBox and QLineEdit with new layout.
        :return: None
        """
        # main widget layout
        # noinspection PyTypeChecker
        layout: QVBoxLayout = self.findChild(QVBoxLayout)
        layout.removeWidget(self.combo_box)

        combo_box_layout = QVBoxLayout()
        combo_box_layout.addWidget(QLabel("Algorithm"))
        combo_box_layout.addWidget(self.combo_box)
        self.combo_box.setMinimumWidth(130)

        line_edit_layout = QVBoxLayout()
        line_edit_layout.addWidget(QLabel("Algorithm"))
        line_edit_layout.addWidget(self.line_edit)

        calculate_button = PushIconButton(
            icon=qta.icon("msc.file-binary"), label="Calculate", small=True
        )
        calculate_button.setToolTip(
            "Calculate the file hash using the selected algorith"
        )
        # noinspection PyUnresolvedReferences
        calculate_button.clicked.connect(self.on_compute_hash)
        calculate_button.setObjectName("calculate_button")

        # new vertical container
        sub_layout = QHBoxLayout()
        sub_layout.setContentsMargins(0, 0, 0, 0)
        sub_layout.addLayout(combo_box_layout)
        sub_layout.addLayout(line_edit_layout)
        sub_layout.addWidget(calculate_button)
        sub_layout.setAlignment(calculate_button, Qt.AlignBottom)
        layout.addLayout(sub_layout)

    def get_value(self) -> dict[str, str]:
        """
        Returns the checksum dictionary.
        :return: A dictionary with the algorithm name and hash.
        """
        algorithm = super().get_value()
        hash = self.line_edit.text()

        # return empty dictionary if the algorithm and hash are not set
        if algorithm is None or not hash:
            return {}

        return {algorithm: hash}

    def validate(self, name: str, label: str, value: Any) -> FormValidation:
        """
        Checks that the both algorithm and hash are provided.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value. Not used.
        :return: The FormValidation instance.
        """
        algorithm = super().get_value()
        hash = self.line_edit.text()

        # field is optional
        if algorithm is None and not hash:
            self.logger.debug("Field not set. Validation passed")
            return FormValidation(validation=True)

        # algorithm not set, but hash is
        if algorithm is None and hash:
            self.logger.debug("Validation failed")
            return FormValidation(
                validation=False,
                error_message="You must select the algorithm name you used to "
                + "generate the hash",
            )

        # hash not set, but algorithm is
        if algorithm is not None and not hash:
            self.logger.debug("Validation failed")
            return FormValidation(
                validation=False,
                error_message="You must provide the hash for the selected algorithm",
            )

        self.logger.debug("Validation passed")
        return FormValidation(validation=True)

    def reset(self) -> None:
        """
        Resets the widget by setting the algorithm to None and emptying the has field.
        """
        super().reset()
        self.line_edit.setText("")

    @Slot()
    def on_compute_hash(self) -> None:
        """
        Compute the hash and populate the hash field.
        :return: None
        """
        self.form: "ModelComponentForm"
        # noinspection PyTypeChecker
        button: PushIconButton = self.findChild(
            PushIconButton, "calculate_button"
        )
        button.setEnabled(False)
        or_text = button.text()
        button.setText("Calculating")

        # get file name
        file_field = self.form.find_field_by_name("url")
        # noinspection PyTypeChecker
        line_edit: QLineEdit = file_field.findChild(QLineEdit)
        file_name = file_field.value()

        self.logger.debug(f"Starting hash calculation using '{file_name}'")
        if file_name and not os.path.isabs(file_name):
            file_name = self.form.model_config.normalize_file_path(file_name)
            self.logger.debug(f"Converted path to absolute: '{file_name}'")

        algorithm = super().get_value()
        # algorith not set
        if algorithm is None:
            QMessageBox.critical(
                self,
                "Error",
                "You must select an algorithm to calculate the file hash",
                QMessageBox.StandardButton.Ok,
            )
        # file name not available or url field is hidden
        elif not file_name or not line_edit.isVisible():
            QMessageBox.critical(
                self,
                "Error",
                "The hash can be only calculated for an external file provided in the "
                "URL field",
                QMessageBox.StandardButton.Ok,
            )
        # file does not exist
        elif not Path(file_name).exists():
            QMessageBox.critical(
                self,
                "Error",
                "The file provided in the URL field does not exist",
                QMessageBox.StandardButton.Ok,
            )
        # calculate hash
        else:
            if not os.path.isabs(file_name):
                file_name = self.form.model_config.normalize_file_path(
                    file_name
                )
                self.logger.debug("Converted path to absolute")

            answer = QMessageBox.warning(
                self,
                "Warning",
                "The hash calculation may take some seconds depending on the "
                + "file size\n\n"
                "Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.No:
                return

            # noinspection PyBroadException
            try:
                self.logger.debug(
                    f"Calculating hash using '{file_name}' with '{algorithm}'"
                )
                hash = self.compute_file_hash(algorithm, file_name)
                self.line_edit.setText(hash)
                self.logger.debug(f"Hash set to '{hash}'")
            except Exception:
                self.logger.debug(
                    "Cannot calculate the file hash due to Exception: "
                    + f"{traceback.print_exc()}"
                )
                QMessageBox.critical(
                    self,
                    "Error",
                    "An error occurred while calculating the hash",
                    QMessageBox.StandardButton.Ok,
                )

        button.setEnabled(True)
        button.setText(or_text)

    @staticmethod
    def compute_file_hash(algorithm: str, file: str) -> str:
        """
        Compute the hash of a file using hashlib
        :param algorithm: The algorithm name (see hashlib).
        :param file: The path to the file.
        :return: The hash
        """
        h = hashlib.new(algorithm)

        with io.open(file, mode="rb") as fh:
            for chunk in iter(lambda: fh.read(io.DEFAULT_BUFFER_SIZE), b""):
                h.update(chunk)

        return h.hexdigest()
