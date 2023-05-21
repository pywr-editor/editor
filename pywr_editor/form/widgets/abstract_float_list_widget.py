from typing import Type, TypeVar

from PySide6.QtWidgets import QHBoxLayout, QLineEdit

from pywr_editor.form import FormCustomWidget, FormField, FormValidation
from pywr_editor.utils import Logging

"""
 This widget handles form fields whose value can be a number and/or
 a list. If a list, the value is converted to a comma-separated list
 of numbers.

 The widget can be configured to:
  - handle numbers and list of numbers
  - handle only list of numbers
  - handle specific types of numbers
  - handle specific types of numbers in the list
"""

value_type = TypeVar("value_type", bound=int | float | list[float | int] | None)


class AbstractFloatListWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: value_type,
        items_count: int = None,
        allowed_item_types: tuple | tuple[Type] | Type = (float, int),
        only_list: bool = False,
        final_type: callable = float,
        allowed_empty: bool = True,
        log_name: str | None = None,
        parent: FormField = None,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The field value.
        :param items_count: The number of items 'value' must contain when it is a
        comma-separated list. When provided the widget checks that the list always
        contain "items_count" items.
        :param allowed_item_types: The type of allowed numbers as tuple types. Default
        to (int, float)
        :param only_list: If True only list are allowed as input and final values. The
        widget always checks that the list contains valid types specified in
        allowed_item_types. If False, list and types specified in allowed_item_types
        are allowed.
        :param final_type: The type of number to convert the final value(s) to. Default
        to float. If only_list is True, the widget checks that the items in the list
        are of final_type.
        :param allowed_empty: Allowed field to be empty during validation. Default to
        True.
        :param log_name: The name to use in the logger.
        :param parent: The parent widget.
        """
        if log_name is None:
            log_name = self.__class__.__name__

        self.logger = Logging().logger(log_name)
        self.logger.debug(f"Loading widget with value {value}")
        self.warning_message = None
        self.items_count = items_count
        self.final_type = final_type
        self.allowed_item_types = allowed_item_types
        self.only_list = only_list
        self.allowed_empty = allowed_empty

        # convert to tuple if it is not
        if not isinstance(self.allowed_item_types, tuple):
            self.allowed_item_types = (self.allowed_item_types,)
        self._allowed_list_item_types = self.allowed_item_types
        # list only
        if self.only_list:
            self.allowed_item_types = ()

        super().__init__(name, value, parent)

        # add widgets
        self.value, self.warning_message = self.sanitise_value(value)
        self.line_edit = QLineEdit()
        self.line_edit.setObjectName(f"{name}_line_edit")

        # set layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)

        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        self.line_edit.setText(self.value)
        self.form_field.set_warning_message(self.warning_message)

    def sanitise_value(self, value: value_type) -> [str | None, str | None]:
        """
        Sanitises the value. The value is converted to a string or comma-separated list
        of strings.
        :param value: The value to sanitise.
        :return: The sanitised value and the warning message.
        """
        self.logger.debug(f"Sanitising value '{value}'")

        message = None
        # value is not a string or a list
        if value is not None and (
            isinstance(value, bool)
            or isinstance(value, self.allowed_item_types + (list,)) is False
        ):
            message = "The value set in the model configuration is not valid"
        elif isinstance(value, list):
            # if list check size and item types
            if (self.items_count is not None and len(value) != self.items_count) or (
                self.allowed_empty is False and len(value) == 0
            ):
                # list is empty or too short
                message = (
                    "The number of values set in the model configuration must "
                    + f"be {self.items_count}, but "
                )
                if len(value) == 1:
                    message += "1 value was given"
                else:
                    message += f"{len(value)} values were given"
            elif (
                all([isinstance(v, self._allowed_list_item_types) for v in value])
                is False
            ):
                type_name = [
                    cls_type.__name__ for cls_type in self._allowed_list_item_types
                ]
                type_name = ", ".join(type_name)
                message = (
                    "The values set in the model configuration must be all "
                    + f"valid numbers ({type_name})"
                )
        # number may be mandatory
        else:
            if value is None:
                self.logger.debug("Value is None. Returning default value")
                return self.get_default_value(), None

        # return None if the values are incorrect
        if message is not None:
            self.logger.debug(message + ". Returning default value")
            return self.get_default_value(), message
        else:
            # convert number or list to a string
            if isinstance(value, list):
                # force to a number
                value = map(self.final_type, value)
                value = ", ".join(map(str, value))
            else:
                value = str(value)
            return value, message

    def get_value(self) -> value_type:
        """
        Returns the value.
        :return: A number or a list of numbers, if the value set in the QLineEdit is
        valid. None otherwise.
        """
        field_value = self.line_edit.text()

        if field_value.strip() == "":
            return self.get_default_value()
        # value is a number
        elif "," not in field_value:
            try:
                # force number to list
                if self.only_list:
                    return [self.final_type(field_value)]
                return self.final_type(field_value)
            except (ValueError, TypeError):
                return self.get_default_value()
        # value is a list
        else:
            # noinspection PyBroadException
            try:
                value_as_list = field_value.split(",")
                if (
                    self.items_count is not None
                    and len(value_as_list) != self.items_count
                ):
                    return self.get_default_value()
                # remove spaces and convert to number
                return [self.final_type(v.strip()) for v in value_as_list]
            except Exception:
                return self.get_default_value()

    def validate(
        self,
        name: str,
        label: str,
        value: value_type,
    ) -> FormValidation:
        """
        Checks that the value is valid.
        :param name: The field name.
        :param label: The field label.
        :param value: The field label. This is not used.
        :return: The FormValidation instance.
        """
        self.logger.debug("Validating field")
        field_value = self.line_edit.text()

        # empty value not allowed
        if self.allowed_empty is False and field_value.strip() == "":
            self.logger.debug("Value cannot be empty")
            return FormValidation(
                validation=False,
                error_message="You must provide a value",
            )
        # empty value allowed, skip validation
        if self.allowed_empty is True and field_value.strip() == "":
            self.logger.debug("Value is empty")
            return FormValidation(
                validation=True,
            )

        # value is a number
        if "," not in field_value:
            self.logger.debug("Value is a number")
            try:
                self.final_type(field_value)
                self.logger.debug("Validation passed")
                return FormValidation(validation=True)
            except (ValueError, TypeError):
                return FormValidation(
                    validation=False,
                    error_message="The value must be a valid number",
                )
        # value is a list
        else:
            # noinspection PyBroadException
            try:
                value_as_list = field_value.split(",")
                if (
                    self.items_count is not None
                    and len(value_as_list) != self.items_count
                ):
                    return FormValidation(
                        validation=False,
                        error_message=f"The list must contains {self.items_count} "
                        + f"values, but {len(value_as_list)} were given",
                    )
                [self.final_type(v.strip()) for v in value_as_list]
                self.logger.debug("Validation passed")
                return FormValidation(validation=True)
            except Exception:
                return FormValidation(
                    validation=False,
                    error_message="The list must contain valid numbers",
                )

    def get_default_value(self) -> None:
        """
        The field default value.
        :return: Returns None.
        """
        return None

    def reset(self) -> None:
        """
        Resets the widget. This empties the QLineEdit widget.
        :return: None
        """
        self.line_edit.setText("")
