from typing import Any, Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QDialogButtonBox,
    QPushButton,
    QWidget,
)
from pywr_editor.form import (
    ExternalDataPickerFormWidget,
    Form,
    FormTitle,
    FormField,
    FormCustomWidget,
)
from pywr_editor.model import ModelConfig

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
        if issubclass(parent.__class__, (Form, FormField, FormCustomWidget)):
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
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Close
        )
        # noinspection PyTypeChecker
        save_button: QPushButton = button_box.findChild(QPushButton)
        save_button.setObjectName("save_button")
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(self.reject)

        # Form
        self.form = ExternalDataPickerFormWidget(
            external_data_dict=external_data_dict,
            model_config=model_config,
            save_button=save_button,
            after_save=after_form_save,
            parent=self,
        )
        # noinspection PyUnresolvedReferences
        button_box.accepted.connect(self.form.on_save)

        # Layout
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.form)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setWindowTitle(title.text())
        self.setMinimumSize(600, 600)
