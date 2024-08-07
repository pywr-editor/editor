from typing import Any, Callable

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from pywr_editor.form import Form, FormField, FormTitle, FormWidget
from pywr_editor.model import ModelConfig
from pywr_editor.widgets import PushIconButton

from .dictionary_item_form_widget import DictionaryItemFormWidget


class DictionaryItemDialogWidget(QDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        dict_key: str | None = None,
        dict_value: str | None = None,
        after_form_save: Callable[[str | dict[str, Any]], None] | None = None,
        additional_data: Any | None = None,
        parent: QWidget | None = None,
    ):
        """
        Initialises the modal dialog.
        :param model_config: The model configuration instance.
        :param dict_key: The dictionary key.
        :param dict_value: The dict_value key.
        :param after_form_save: A function to execute after the form is saved. This
        receives the form data.
        :param additional_data: Any additional data to store in the form.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)

        # check parent
        if issubclass(parent.__class__, (Form, FormField, FormWidget)):
            raise ValueError(
                f"The parent '{parent}' cannot be a form component already instantiated"
            )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Dialog title and description
        title = FormTitle("Dictionary configuration")
        description = QLabel("Configure the dictionary key and its value")

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
        self.form = DictionaryItemFormWidget(
            model_config=model_config,
            dict_key=dict_key,
            dict_value=dict_value,
            save_button=save_button,
            after_save=after_form_save,
            additional_data=additional_data,
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
        self.setMinimumSize(650, 500)
        self.setWindowModality(Qt.WindowModality.WindowModal)
