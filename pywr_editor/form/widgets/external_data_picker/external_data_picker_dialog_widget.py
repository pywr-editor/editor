from typing import Any, Callable

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from pywr_editor.form import (
    ExternalDataPickerFormWidget,
    Form,
    FormField,
    FormTitle,
    FormWidget,
)
from pywr_editor.model import ModelConfig
from pywr_editor.widgets import PushIconButton

"""
 This widgets shows a dialog with a form to configure
 a dictionary with instructions to fetch external data
 using Pywr load_parameter_values and load_dataframe
 helper functions.

 Some parameters (such as InterpolatedVolumeParameter)
 can fetch data from a model table or an external file
 using Pandas.
"""


class ExternalDataPickerDialogWidget(QDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        external_data_dict: dict[str, Any] | None,
        after_form_save: Callable[[str | dict[str, Any]], None] | None = None,
        parent: QWidget | None = None,
    ):
        """
        Initialises the modal dialog.
        :param model_config: The model configuration instance.
        :param external_data_dict: The dictionary containing the instructions to fetch
        external data using Pywr.
        :param after_form_save: A function to execute after the form is saved. This
        receives the form data.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)

        # check parent
        if issubclass(parent.__class__, (Form, FormField, FormWidget)):
            raise ValueError(
                "The parent cannot be a form component already instantiated"
            )

        # form must have a valid ParameterConfig instance
        if external_data_dict is None:
            external_data_dict = {}

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Dialog title and description
        title = FormTitle("Fetch external data")
        description = QLabel(
            "Define how to fetch external data using an existing model table or by "
            + "specifying an external file"
        )

        # Buttons
        button_box = QHBoxLayout()
        close_button = PushIconButton(icon=qta.icon("msc.close"), label="Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(self.reject)

        save_button = PushIconButton(icon=qta.icon("msc.save"), label="Save")
        save_button.setObjectName("save_button")

        button_box.addStretch()
        button_box.addWidget(save_button)
        button_box.addWidget(close_button)

        # Form
        self.form = ExternalDataPickerFormWidget(
            external_data_dict=external_data_dict,
            model_config=model_config,
            save_button=save_button,
            after_save=after_form_save,
            parent=self,
        )
        # noinspection PyUnresolvedReferences
        save_button.clicked.connect(self.form.on_save)

        # Layout
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.form)
        layout.addLayout(button_box)

        self.setLayout(layout)
        self.setWindowTitle(title.text())
        self.setMinimumSize(600, 600)
        self.setWindowModality(Qt.WindowModality.WindowModal)
