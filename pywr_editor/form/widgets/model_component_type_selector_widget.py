import os
from typing import TYPE_CHECKING, Literal, Union

from PySide6.QtCore import QSize, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy

import pywr_editor.dialogs
import pywr_editor.model
from pywr_editor.form import FormCustomWidget, FormField, FormSection
from pywr_editor.model import ParameterConfig, RecorderConfig
from pywr_editor.utils import Logging
from pywr_editor.widgets import ComboBox, PushIconButton

if TYPE_CHECKING:
    from pywr_editor.form import ParameterForm, RecorderForm

"""
 ComboBox that shows a list of model components (parameters or recorders)
 types. The ComboBox items include all pywr built-in components and any custom
 component declared in the JSON "includes" field.

 Component types can also be filtered to show only specific ones. When a filter is
 set with this widget, a custom imported type:
  - will always be shown, when it is not imported in the "includes" field.
  - will be shown, if the type is the direct parent of a class provided
    in the filter, when the type is imported in the "includes" field.
"""


class ModelComponentTypeSelectorWidget(FormCustomWidget):
    section_added = Signal()

    def __init__(
        self,
        component_type: Literal["parameter", "recorder"],
        name: str,
        value: ParameterConfig | RecorderConfig,
        parent: FormField,
        include_comp_key: list[str],
        log_name: str,
    ):
        """
        Initialises the widget to select the component type.
        :param component_type: The model component type. It can be "parameter",
        oe "recorder".
        :param name: The field name.
        :param value: The configuration instance of the selected component
        (ParameterConfig for parameters or RecorderConfig for recorders).
        :param parent: The parent widget.
        :param include_comp_key: A list of strings representing component keys to only
        include in the widget. For example "index" for parameters to include all
        types inheriting from IndexParameter. An error will be shown if a not allowed
        type is used as value.
        :param log_name: THe name of the log.
        """
        self.logger = Logging().logger(log_name)
        self.logger.debug(f"Loading widget with {component_type}: {value}")
        self.logger.debug(f"Using the following keys {include_comp_key}")
        self.type = component_type
        self.form: Union["ParameterForm", "RecorderForm"]

        # check arguments
        if self.type not in ["parameter", "recorder"]:
            raise ValueError(
                "The component type can only be: 'parameters' or 'recorders'"
            )
        if self.is_parameter_type and not isinstance(value, ParameterConfig):
            raise ValueError(
                "The value can only be an instance of ParameterConfig"
            )
        elif self.is_recorder_type and not isinstance(value, RecorderConfig):
            raise ValueError(
                "The value can only be an instance of RecorderConfig"
            )

        super().__init__(name, value, parent)
        self.init = True

        icon_class = None
        pywr_data_attr = None
        config_class = None
        if self.is_parameter_type:
            self.pywr_comp_data = self.form.model_config.pywr_parameter_data
            self.default_comp_type = "constant"
            pywr_data_attr = "parameters"
            self.import_method = "get_custom_parameters"
            icon_class = "ParameterIcon"
            config_class = "ParameterConfig"
            self.custom_section_name = "CustomParameterSection"
        elif self.is_recorder_type:
            self.pywr_comp_data = self.form.model_config.pywr_recorder_data
            self.default_comp_type = "node"
            pywr_data_attr = "recorders"
            self.import_method = "get_custom_recorders"
            icon_class = "RecorderIcon"
            config_class = "RecorderConfig"
            self.custom_section_name = "CustomRecorderSection"

        icon_class = getattr(pywr_editor.widgets, icon_class)
        self.custom_imports = self.form.model_config.includes

        # Collect all pywr and custom component types
        self.all_components = {
            **getattr(self.pywr_comp_data, pywr_data_attr),
            **getattr(self.custom_imports, self.import_method)(),
        }

        # check if the type exists
        if include_comp_key:
            for comp_type in include_comp_key:
                if comp_type not in self.all_components.keys():
                    raise ValueError(
                        f"The {self.type} type '{comp_type}' does not exist. Available "
                        + f"types are: {', '.join(self.all_components.keys())}"
                    )
            # change default_comp_type when filter is provided
            self.default_comp_type = include_comp_key[0]

            self.logger.debug(
                f"Including only the following {self.type} keys: {include_comp_key}"
            )

        # button to pywr API
        self.doc_button = PushIconButton(icon=":/misc/help", parent=self)
        self.doc_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.doc_button.setToolTip(
            f"Open the pywr manual page for this {self.type}"
        )
        self.doc_button.setEnabled(False)
        # noinspection PyUnresolvedReferences
        self.doc_button.clicked.connect(self.on_doc_button_click)
        self.doc_button.setMaximumWidth(30)

        # populate the field with the available components - key does not have
        # component suffix
        self.combo_box = ComboBox()
        self.combo_box.setIconSize(QSize(15, 15))

        # collect all pywr and custom component types
        for key, info in self.all_components.items():
            # filter component keys
            if include_comp_key is not None and key not in include_comp_key:
                continue

            self.combo_box.addItem(
                QIcon(icon_class(key)),
                info["name"],
                key,  # TODO fix icon with high-DPI screens
            )
        # always add custom components not defined in the model "includes" key
        self.combo_box.addItem(
            QIcon(icon_class("★")),
            f"Custom {self.type} (not imported)",
            f"custom_{self.type}",
        )

        comp_key = value.key
        self.logger.debug(f"{self.type.title()} key is: {comp_key}")
        is_name_valid = comp_key in self.all_components.keys()

        # select active component type
        index = self.combo_box.findData(comp_key)
        # name is in combo box (can be a pywr or custom loaded component)
        if index != -1:
            self.logger.debug(f"Setting combo box index {index}")
            self.combo_box.setCurrentIndex(index)

            doc_url = self.pywr_comp_data.get_doc_url_from_key(comp_key)
            self.doc_button.setProperty(
                "url", self.pywr_comp_data.get_doc_url_from_key(comp_key)
            )
            if doc_url is not None:
                self.doc_button.setEnabled(True)
        # index not found: unknown custom component or type not allowed (for a pywr or
        # custom loaded component) or missing component key (type not provided)
        else:
            self.logger.debug(f"Index is invalid ({index})")
            # loaded custom or pywr built-in component that is not in the combo box
            # because it is not allowed or component key is None
            if is_name_valid or not comp_key:
                # set value to default
                self.logger.debug(f"Selecting {self.default_comp_type}")
                self.value = getattr(pywr_editor.model, config_class)(
                    props={"type": self.default_comp_type}
                )
                self.reset()
                # do not warn if type is not provided
                if comp_key:
                    message = f"The {self.type} type set in the model configuration is "
                    message += "not allowed"
                    self.logger.debug(f"{message}. Key is {comp_key}")
                    self.form_field.set_warning_message(message)
            # custom components not provided in the "includes" key
            else:
                self.combo_box.setCurrentIndex(
                    self.combo_box.findData(f"custom_{self.type}")
                )
                self.logger.debug(
                    f"The {self.type} type is not recognised. Selected Custom "
                    + self.type.title()
                )

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)
        layout.addWidget(self.doc_button)

        # run action after all fields are available and whole form has loaded
        self.form.after_render_actions.append(self.after_field_render)

    def after_field_render(self) -> None:
        """
        Action called after the form has been rendered.
        :return: None
        """
        # init form
        self.add_component_section(self.value.key)

        # noinspection PyUnresolvedReferences
        self.combo_box.currentIndexChanged.connect(self.on_type_change)

        self.init = False

        # hide field if only one component type can be selected
        if len(self.combo_box.all_items) == 1:
            self.form.change_field_visibility(
                name=self.form_field.name, show=False, clear_message=False
            )

    def add_component_section(self, comp_key: str) -> None:
        """
        Adds a new form section corresponding to the component key.
        :param comp_key: The component key.
        :return: None
        """
        pywr_class = self.pywr_comp_data.get_class_from_type(comp_key)
        self.form: Union["ParameterForm", "RecorderForm"]

        # key not provided - section for default component is selected
        if comp_key is None:
            self.logger.debug(f"{self.type.title()} key is None")
        # key is provided but type is not a pywr built-in component - custom component
        elif pywr_class is None:  # custom component
            self.logger.debug(f"{self.type.title()} '{comp_key}' is custom")
            # imported Python class
            if (
                comp_key
                in getattr(self.custom_imports, self.import_method)().keys()
            ):
                self.logger.debug(
                    f"{self.type.title()} is included as custom import"
                )
                self.form.section_form_data["imported"] = True
            # unknown class
            else:
                self.logger.debug(
                    f"{self.type.title()} is not included as custom import"
                )
            self.logger.debug(
                f"Adding section for '{self.custom_section_name}'"
            )
            # noinspection PyTypeChecker
            self.form.add_section_from_class(
                getattr(pywr_editor.dialogs, self.custom_section_name),
                self.form.section_form_data,
            )
        # section for pywr built-in component
        elif hasattr(pywr_editor.dialogs, f"{pywr_class}Section"):
            self.logger.debug(f"Adding section for '{comp_key}'")
            self.form.add_section_from_class(
                getattr(pywr_editor.dialogs, f"{pywr_class}Section"),
                self.form.section_form_data,
            )
        else:
            raise ValueError(f"Cannot add section for '{comp_key}'")

        # noinspection PyUnresolvedReferences
        self.section_added.emit()

    @Slot(int)
    def on_type_change(self, index: int) -> None:
        """
        Slot called when the ComboBox value changes.
        :param index: The selected item index.
        :return: None
        """
        comp_key = self.combo_box.itemData(index)

        # handle sections
        # noinspection PyTypeChecker
        current_section: FormSection = self.form.findChild(FormSection)
        if current_section is not None:
            self.form.delete_section(current_section)
            self.logger.debug(f"Deleted section '{current_section.name}'")
            del current_section
        self.add_component_section(comp_key)

        # update the doc url if available
        doc_url = self.pywr_comp_data.get_doc_url_from_key(comp_key)
        # noinspection PyTypeChecker
        self.doc_button.setProperty(
            "url", self.pywr_comp_data.get_doc_url_from_key(comp_key)
        )
        if doc_url is None:
            self.doc_button.setEnabled(False)
        else:
            self.doc_button.setEnabled(True)

        # Trigger reset of common fields (shared by sections) and Slots after field
        # is initialised
        if self.init is False:
            for name in ["url", "table", "value", "values"]:
                self.logger.debug(f"Resetting FormField '{name}'")
                form_field = self.form.find_field_by_name(name)
                # ignore non-existing fields
                if form_field is not None:
                    # noinspection PyUnresolvedReferences
                    form_field.widget.reset()
                    form_field.clear_message()

    @Slot()
    def on_doc_button_click(self) -> None:
        """
        Opens the URL to the pywr documentation for the selected component, when
        available.
        :return: None
        """
        # noinspection PyTypeChecker
        url = self.doc_button.property("url")
        if url is not None:
            os.startfile(url)

    def get_value(self) -> str:
        """
        Returns the data for the selected field value.
        :return: The field data representing the pywr component key.
        """
        return self.combo_box.currentData()

    def reset(self) -> None:
        """
        Reset the widget by removing the current section and adding the default
        section.
        :return: None
        """
        default_index = self.combo_box.findData(self.default_comp_type)

        # Reset the selected index in case the default index is still the same
        self.combo_box.blockSignals(True)
        self.combo_box.setCurrentIndex(-1)
        self.combo_box.blockSignals(False)

        if default_index != -1:
            # this changes the combo box value and renders the new section
            self.combo_box.setCurrentIndex(default_index)

    @property
    def is_parameter_type(self) -> bool:
        """
        Checks that the type is parameter.
        :return: True if the component type is parameter.
        """
        return self.type == "parameter"

    @property
    def is_recorder_type(self) -> bool:
        """
        Checks that the type is recorder.
        :return: True if the component type is recorder.
        """
        return self.type == "recorder"
