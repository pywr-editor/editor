from typing import TYPE_CHECKING, Literal

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import FormField, FormWidget, Validation
from pywr_editor.utils import Logging
from pywr_editor.widgets import ComboBox, ParameterIcon, RecorderIcon

if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentForm

"""
 This widgets displays a list of available model components
 (i.e. recorders or parameters registered in the respective
 keys in the JSON file) and allows the user to pick one.

 Component types can also be filtered to show only
 the allowed ones.
"""


class AbstractStringModelComponentPickerWidget(FormWidget):
    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
        component_type: Literal["parameter", "recorder"],
        include_comp_key: list[str] | None = None,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected component name.
        :param parent: The parent widget.
        :param component_type: The component type (parameter or recorder).
        :param include_comp_key: A list of strings representing component keys to only
        include in the widget. An error will be shown if a not-allowed component type
        is used as value.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")
        super().__init__(name, value, parent)

        self.component_type = component_type

        # model data
        self.form: "ModelComponentForm"
        self.model_config = self.form.model_config
        if self.is_parameter:
            self.comp_data = self.model_config.pywr_parameter_data
            model_prop = self.model_config.parameters
            model_comp_names = list(model_prop.get_all().keys())
            include_method = self.model_config.includes.get_custom_parameters
            icon_class = ParameterIcon
        elif self.is_recorder:
            self.comp_data = self.model_config.pywr_recorder_data
            model_prop = self.model_config.recorders
            model_comp_names = list(model_prop.get_all().keys())
            include_method = self.model_config.includes.get_custom_recorders
            icon_class = RecorderIcon
        else:
            raise ValueError("The component_type can only be 'parameter' or 'recorder'")

        # check if the component type exists
        all_comp_keys = self.comp_data.keys + list(include_method().keys())
        if include_comp_key:
            for comp_type_key in include_comp_key:
                if comp_type_key not in all_comp_keys:
                    raise ValueError(
                        f"The {component_type} type '{comp_type_key}' does not exist. "
                        + f"Available types are: {', '.join(all_comp_keys)}"
                    )

            self.logger.debug(f"Including only the following keys: {include_comp_key}")

        # add component names with icon
        self.combo_box = ComboBox()
        self.combo_box.addItem("None")
        for name in model_comp_names:
            param_obj = model_prop.config(name, as_dict=False)
            key = param_obj.key

            # filter component keys
            if include_comp_key is not None and key not in include_comp_key:
                continue

            self.combo_box.addItem(QIcon(icon_class(key)), name, key)

        # set selected
        if value is None or value == "":
            self.logger.debug("Value is None or empty. No value set")
        # wrong type
        elif not isinstance(value, str):
            self.field.set_warning(f"The {component_type} name must be a string")
        # component name exists
        elif value in model_comp_names:
            # check if the component is allowed when the filter is provided
            if value not in self.combo_box.all_items:
                self.field.set_warning(
                    f"The type of selected {component_type} set in the model "
                    "configuration is not allowed"
                )
            else:
                self.logger.debug(f"Setting '{value}' as selected {component_type}")
                self.combo_box.setCurrentText(value)
        else:
            self.field.set_warning(
                f"The {component_type} named '{value}' does not exist in the "
                "model configuration"
            )

        # no model components - overwrite any previous message
        if len(self.combo_box.all_items) == 1:
            self.field.set_warning(
                f"There are no {component_type}s available. Add a new {component_type} "
                "first before setting up this option"
            )

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

    def get_value(self) -> str:
        """
        Returns the selected component name.
        :return: The component name.
        """
        return self.combo_box.currentText()

    def validate(self, name: str, label: str, value: str) -> Validation:
        """
        Validates the value.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The instance of Validation
        """
        if value == "None":
            return Validation(f"You must select a model {self.component_type}")
        return Validation()

    def reset(self) -> None:
        """
        Reset the widget by selecting no component.
        :return: None
        """
        self.combo_box.setCurrentText("None")

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
