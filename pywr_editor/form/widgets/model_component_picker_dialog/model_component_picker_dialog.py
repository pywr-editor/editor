from typing import Any, Callable, Literal, TypeVar

import qtawesome as qta
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import pywr_editor
from pywr_editor.form import Form, FormField, FormTitle, FormWidget
from pywr_editor.model import ModelConfig, ParameterConfig, RecorderConfig
from pywr_editor.utils import Logging
from pywr_editor.widgets import PushIconButton

after_form_save_type = TypeVar(
    "after_form_save_type", bound=Callable[[str | dict[str, Any]], None] | None
)


class ModelComponentPickerDialog(QDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        component_obj: ParameterConfig | RecorderConfig | None,
        component_type: Literal["parameter", "recorder"],
        after_form_save: after_form_save_type = None,
        additional_data: Any | None = None,
        parent: QWidget | None = None,
    ):
        """
        Initialises the modal dialog.
        :param model_config: The model configuration instance.
        :param component_obj: The instance of ParameterConfig or RecorderConfig for the
        selected component.
        :param component_type: The component type (parameter or recorder).
        :param after_form_save: A function to execute after the form is saved.
        This receives the form data.
        :param additional_data: Any additional data to store in the form.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)

        self.component_type = component_type
        self.after_form_save = after_form_save
        self.additional_data = additional_data

        if not self.is_parameter and not self.is_recorder:
            raise ValueError("The component_type can only be 'parameter' or 'recorder'")

        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading dialog for {component_type}")

        # check parent
        if issubclass(parent.__class__, (Form, FormField, FormWidget)):
            raise ValueError(
                "The parent cannot be a form component already instantiated"
            )

        # form must have a valid config instance
        if component_obj is None:
            if self.is_parameter:
                component_obj = getattr(pywr_editor.model, "ParameterConfig")(props={})

            elif self.is_recorder:
                component_obj = getattr(pywr_editor.model, "RecorderConfig")(props={})

        # get component keys to filter
        include_comp_key = None
        if additional_data and "include_comp_key" in additional_data:
            include_comp_key = additional_data["include_comp_key"]

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Dialog title and description
        title = FormTitle(f"Select a {component_type}")
        description = QLabel(
            f"Select an existing model {component_type} or define a new one by "
            + "loading data from an external file or a table"
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
        if self.is_parameter:
            form_class = "ParameterPickerFormWidget"
        elif self.is_recorder:
            form_class = "RecorderPickerFormWidget"
        else:
            raise ValueError

        self.form = getattr(pywr_editor.form, form_class)(
            component_obj=component_obj,
            model_config=model_config,
            save_button=save_button,
            include_comp_key=include_comp_key,
            parent=self,
        )
        # noinspection PyUnresolvedReferences
        save_button.clicked.connect(self.on_save)

        # Layout
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.form)
        layout.addLayout(button_box)

        self.setLayout(layout)
        self.setWindowTitle(title.text())
        self.setMinimumSize(600, 600)
        self.setWindowModality(Qt.WindowModality.WindowModal)

    @Slot()
    def on_save(self) -> None:
        """
        Slot called when user clicks on the "Save" button. The form data are sent to
        self.after_form_save().
        :return: None
        """
        self.logger.debug("Saving form")
        source_widget = self.form.find_field("comp_source").widget

        form_data = self.form.save()
        if form_data is False:
            return

        # model component
        if form_data["comp_source"] == source_widget.labels["model_component"]:
            form_data = form_data["comp_name"]
        # anonymous component
        else:
            del form_data["comp_source"]

        # enable the save button in the parent dialog
        save_button: QPushButton = self.parent().findChild(QPushButton, "save_button")
        if save_button:
            save_button.setEnabled(True)

        # callback function
        self.after_form_save(form_data, self.additional_data)

    @property
    def is_parameter(self) -> bool:
        """
        Returns True if the component type is a parameter.
        :return: True if the type is a parameter, False otherwise
        """
        return self.component_type == "parameter"

    @property
    def is_recorder(self) -> bool:
        """
        Returns True if the component type is a recorder.
        :return: True if the type is a recorder, False otherwise
        """
        return self.component_type == "recorder"
