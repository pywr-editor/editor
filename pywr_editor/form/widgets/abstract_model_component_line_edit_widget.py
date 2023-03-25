from typing import TYPE_CHECKING, Any, Literal

import qtawesome as qta
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLineEdit

from pywr_editor.form import (
    FormCustomWidget,
    FormValidation,
    ModelComponentPickerDialog,
)
from pywr_editor.model import ParameterConfig, RecorderConfig
from pywr_editor.utils import Logging, ModelComponentTooltip, get_signal_sender
from pywr_editor.widgets import ParameterIcon, PushIconButton, RecorderIcon

if TYPE_CHECKING:
    from pywr_editor.form import FormField, ModelComponentForm

"""
 This widget displays a non-editable QLineEdit and
 buttons that allow selecting and existing model
 component (parameter or recorder) or defining a
 new one via a dialog.
"""


class AbstractModelComponentLineEditWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: str | dict | int | float,
        parent: "FormField",
        component_type: Literal["parameter", "recorder"],
        is_mandatory: bool = True,
        include_comp_key: list[str] | None = None,
    ):
        """
        Initialises the widget to select a model component. The component can be a,
        string when it refers to a model component, a dictionary, for anonymous
        component loaded via the "url" or "table" keys, or a number, for a constant
        parameter.
        :param name: The field name.
        :param value: The value describing the component (dictionary, number or
        string).
        :param parent: The parent widget.
        :param component_type: The type of model component (parameter or recorder).
        :param is_mandatory: Whether the component must be provided or the field can
        be left empty. Default to True.
        :param include_comp_key: A string or list of strings representing component
        keys to only include in the widget. An error will be shown if the component
        type provided as value is not allowed. The picker dialog will also filter
        the component types.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")
        self.logger.debug(f"Using the following keys: {include_comp_key}")

        super().__init__(name, value, parent)
        self.form: "ModelComponentForm"
        self.model_config = self.form.model_config
        self.component_type = component_type

        if self.is_parameter:
            self.component_data = self.model_config.pywr_parameter_data
            self._icon_class = ParameterIcon
            self._config_prop = self.model_config.parameters
            self._exist_method = self._config_prop.does_parameter_exist
            self._config_obj = ParameterConfig
            custom_import_method = "get_custom_parameters"
        elif self.is_recorder:
            self.component_data = self.model_config.pywr_recorder_data
            self._icon_class = RecorderIcon
            self._config_prop = self.model_config.recorders
            self._exist_method = self._config_prop.does_recorder_exist
            self._config_obj = RecorderConfig
            custom_import_method = "get_custom_recorders"
        else:
            raise ValueError(
                "The component_data can only be 'parameter' or 'recorder'"
            )
        self.is_mandatory = is_mandatory

        # include only certain component types
        if include_comp_key is not None:
            if isinstance(include_comp_key, str):
                include_comp_key = [include_comp_key]
            # convert to lowercase
            include_comp_key = [key.lower() for key in include_comp_key]

            # check if the component type exists
            all_comp_keys = self.component_data.keys + list(
                getattr(
                    self.model_config.includes, custom_import_method
                )().keys()
            )
            for comp_type in include_comp_key:
                if comp_type not in all_comp_keys:
                    raise ValueError(
                        f"The {self.component_type} type {comp_type} does not exist. "
                        + f"Available types are: {', '.join(all_comp_keys)}"
                    )
            self.logger.debug(
                f"Including only the following {self.component_type} keys: "
                + f"{include_comp_key}"
            )
            # prettified keys
            self.include_comp_names = list(
                map(
                    self.component_data.humanise_name,
                    include_comp_key,
                )
            )
        else:
            self.include_comp_names = None
        self.include_comp_key = include_comp_key

        self.component_obj, self.warning_message = self.sanitise_value(value)

        # field
        self.line_edit = QLineEdit()
        self.line_edit.setReadOnly(True)

        # buttons
        self.select_button = PushIconButton(
            icon=qta.icon("msc.inspect"), label="Select"
        )
        self.select_button.setToolTip(
            f"Select an existing model {self.component_type} or define a new one"
        )
        # noinspection PyUnresolvedReferences
        self.select_button.clicked.connect(self.open_picker_dialog)

        self.clear_button = PushIconButton(
            icon=qta.icon("msc.remove"), label="Clear"
        )
        self.clear_button.setToolTip("Empty the field")
        # noinspection PyUnresolvedReferences
        self.clear_button.clicked.connect(self.reset)

        # main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.select_button)
        layout.addWidget(self.clear_button)

        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        # fill the widget for the first time
        self.on_update_component()

    @Slot()
    def on_update_component(self) -> None:
        """
        Updates the widget with the new component and the warning if present.
        :return:
        """
        self.logger.debug(
            f"Running on_update_component Slot from {get_signal_sender(self)}"
        )

        # reset the icon
        self.reset_icon()

        # update the field
        if self.component_obj is not None:
            # show component type or its name if it is a model component
            if self.is_anonymous_component:
                text = self.component_obj.humanised_type
                self.logger.debug(
                    f"Anonymous {self.component_type}. Setting text {text}"
                )
            else:
                text = self.component_obj.name
                self.logger.debug(
                    f"Model {self.component_type}. Setting text {text}"
                )
            self.line_edit.setText(text)

            if self.component_obj.key is not None:
                self.line_edit.addAction(
                    QIcon(self._icon_class(self.component_obj.key)),
                    QLineEdit.ActionPosition.LeadingPosition,
                )
                tooltip = ModelComponentTooltip(
                    model_config=self.model_config, comp_obj=self.component_obj
                )
                self.line_edit.setToolTip(tooltip.render())
        else:
            self.line_edit.setText("Not set")
            self.line_edit.setToolTip("")

        self.form_field.set_warning_message(self.warning_message)

    def sanitise_value(
        self, value: str | dict | int | float
    ) -> [ParameterConfig | RecorderConfig | None, str | None]:
        """
        Sanitises the value.
        :param value: The value to sanitise.
        :return: A tuple containing (1) the ParameterConfig or RecorderConfig instance
        or None if the value is not valid and (2) the warning message.
        """
        self.logger.debug(f"Sanitising value {value}")
        message = None
        component_obj = None

        # existing model component
        if isinstance(value, str) and value.strip() != "":
            self.logger.debug(
                f"Value is a string. Fetching existing model {self.component_type}"
            )
            if self._exist_method(value) is False:
                message = f"The model {self.component_type} does not exist"
                component_obj = self._config_obj(props={}, name=value)
                self.logger.debug(message)
            else:
                component_obj = self._config_prop.get_config_from_name(
                    value, as_dict=False
                )
                self.logger.debug(
                    f"Using {self.component_type} configuration: {component_obj.props}"
                )
        # parameter is a number
        elif self.is_parameter and isinstance(value, (int, float)):
            self.logger.debug(
                "Value is a number. Converting it to constant anonymous parameter"
            )
            component_obj = ParameterConfig(
                props={"type": "constant", "value": value}
            )
            self.logger.debug(
                f"Using parameter configuration: {component_obj.props}"
            )
        # component is a valid dictionary
        elif isinstance(value, dict) and "type" in value:
            self.logger.debug("Value is a dictionary")
            component_obj = getattr(self._config_prop, self.component_type)(
                config=value, deepcopy=True
            )
        # value not provided
        elif value is None:
            self.logger.debug("Value is not set because it is None")
        # wrong type value
        else:
            message = (
                "The value provided in the model configuration is not valid"
            )
            self.logger.debug(message)

        # check if the component type is allowed
        if (
            self.include_comp_key is not None
            and component_obj is not None
            and component_obj.key is not None
            and component_obj.key not in self.include_comp_key
        ):
            message = (
                f"The type of provided {self.component_type} ("
                + f"{component_obj.humanised_type}) is not allowed. Allowed types "
                + f"are: {', '.join(self.include_comp_names)}"
            )
            self.logger.debug(f"{component_obj.name} is not a valid type")
            # reset object
            component_obj = None

        return component_obj, message

    @property
    def is_anonymous_component(self) -> bool | None:
        """
        Returns True if the component is anonymous. An anonymous component has no name
        and is not defined in the model configuration.
        :return: True if the component is anonymous, False otherwise or None if the
        component is not defined.
        """
        if self.component_obj is not None:
            return self.component_obj.name is None
        else:
            return None

    def get_value(self) -> str | dict | int | float | None:
        """
        Returns the field value.
        :return: A dictionary with the component configuration or the component name,
        if it is defined in the model configuration, or a number, for constant
        parameters, or None if the component is not defined or does not exist.
        """
        if self.component_obj is None:
            return None

        if self.is_anonymous_component is True:
            # for constant parameter from value, return the number instead of the
            # dictionary
            if (
                self.is_parameter
                and self.component_obj.key is not None
                and self.component_obj.key == "constant"
                and "value" in self.component_obj.props
            ):
                return self.component_obj.props["value"]
            else:
                return self.component_obj.props
        # check that the model component exists
        elif self._exist_method(self.component_obj.name):
            return self.component_obj.name

        return None

    def validate(
        self, name: str, label: str, value: str | dict | float | int | None
    ) -> FormValidation:
        """
        Checks that the value is valid.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The FormValidation instance.
        """
        self.logger.debug("Validating field")

        if self.is_mandatory is False:
            self.logger.debug(
                "Skipping validation, because the field is not mandatory"
            )
            return FormValidation(validation=True)

        if value is None:
            return FormValidation(
                validation=False,
                error_message=f"You must provide a valid {self.component_type}",
            )
        return FormValidation(validation=True)

    @Slot()
    def reset(self) -> None:
        """
        Resets the widget. This can also be used as a Slot.
        :return: None
        """
        self.form_field.clear_message()
        self.line_edit.setText("Not set")
        self.line_edit.setToolTip("")
        self.component_obj = None
        self.warning_message = ""

        # remove the icon
        self.reset_icon()

    def reset_icon(self) -> None:
        """
        Resets the icon in the lin edit widget.
        :return: None
        """
        for a in self.line_edit.actions():
            self.line_edit.removeAction(a)

    @Slot()
    def open_picker_dialog(self) -> None:
        """
        Opens the dialog to select a component.
        :return: None
        """
        dialog = ModelComponentPickerDialog(
            model_config=self.model_config,
            component_obj=self.component_obj,
            component_type=self.component_type,
            additional_data={
                "include_comp_key": self.include_comp_key,
            },
            after_form_save=self.on_form_save,
            parent=self.form.parent,
        )
        dialog.open()

    def on_form_save(self, form_data: str | dict[str, Any], _: Any) -> None:
        """
        Updates the component configuration object.
        :param form_data: The form data from ModelComponentPickerDialog.
        :param _: Any additional data. None for this widget.
        :return: None
        """
        self.logger.debug(
            f"Running post-saving action on_form_save with value {form_data}"
        )
        # model component
        if isinstance(form_data, str):
            self.logger.debug(f"Data is a model {self.component_type} (string)")
            self.component_obj = self._config_prop.get_config_from_name(
                form_data, as_dict=False
            )
        # anonymous component
        else:
            self.logger.debug(
                f"Data is an anonymous {self.component_type} (dictionary)"
            )
            self.component_obj = self._config_obj(props=form_data)

        # clear any message
        self.logger.debug("Cleaning message and updated field")
        self.warning_message = ""
        self.form_field.clear_message()

        # update the field
        self.on_update_component()

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
