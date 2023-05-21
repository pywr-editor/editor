from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit

from pywr_editor.form import FormCustomWidget, FormField, FormValidation
from pywr_editor.utils import Logging


class FloatWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: int | float | dict,
        parent: FormField,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        suffix: str | None = None,
    ):
        """
        Initialises the widget that provides a constant float.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent widget.
        :param min_value: The minimum value. Optional.
        :param max_value: The maximum value. Optional.
        :param suffix: A suffix label to add to the field. Optional.
        """
        super().__init__(name, value, parent)
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget {name} with value {value}")

        self.min_value = min_value
        self.max_value = max_value
        self.logger.debug(f"Bounds are [{min_value}-{max_value}]")

        self.line_edit = QLineEdit()
        self.line_edit.setObjectName(f"{name}_line_edit")
        self.line_edit.setMaximumWidth(100)

        self.line_edit.blockSignals(True)
        # value is provided
        if value is not None and isinstance(value, (int, float)):
            self.logger.debug("Value is valid")
            self.line_edit.setText(str(value))

            # check bound
            if min_value is not None and value < min_value:
                message = "The value is below the allowed minimum of " + str(
                    round(min_value, 2)
                )
                self.logger.debug(message)
                self.form_field.set_warning_message(message)
            if max_value is not None and value > max_value:
                message = "The value is above the allowed maximum of " + str(
                    round(max_value, 2)
                )
                self.logger.debug(message)
                self.form_field.set_warning_message(message)
        # otherwise use default if provided
        elif self.get_default_value() is not None:
            self.logger.debug(f"Setting default value of {self.get_default_value()}")
            self.line_edit.setText(str(self.get_default_value()))
        self.line_edit.blockSignals(False)

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        if suffix:
            layout.addWidget(QLabel(suffix))
        layout.addStretch()

    def get_default_value(self) -> float | None:
        """
        The field default value use by self.get_value().
        :return: The default value.
        """
        return self.form_field.default_value

    def get_value(self) -> str | float | None:
        """
        Returns the form field value.
        :return: The form field value. None if the field is empty.
        """
        field_value = self.line_edit.text()
        try:
            return float(field_value)
        except (ValueError, TypeError):
            # returns original value for validation
            return field_value

    def reset(self) -> None:
        """
        Resets the widget. This empties the QLineEdit field or set the field
        default value.
        :return: None
        """
        value = ""
        # restore default if available
        if self.form_field.default_value is not None:
            value = str(self.form_field.default_value)

        self.line_edit.setText(value)

    def validate(self, name: str, label: str, value: float | str) -> FormValidation:
        """
        Checks that the parameter is a valid number.
        :param name: The field name.
        :param label: The field label.
        :param value: The field label.
        :return: True if the field contains a valid number, False otherwise.
        """
        # value is empty or None
        if value is None or value == "":
            self.logger.debug("Value is empty. Validation passed")
            return FormValidation(validation=True)

        try:
            value = float(value)
        except (ValueError, TypeError):
            message = "The value is not a valid number"
            self.logger.debug(message)
            return FormValidation(validation=False, error_message=message)
        else:
            # check bounds
            if self.max_value is not None and value > self.max_value:
                message = (
                    "The value is above the allowed maximum of "
                    + f"{round(self.max_value, 2)}"
                )
                self.logger.debug(message)
                return FormValidation(
                    validation=False,
                    error_message=message,
                )
            if self.min_value is not None and value < self.min_value:
                message = (
                    "The value is below the allowed minimum of "
                    + f"{round(self.min_value, 2)}"
                )
                self.logger.debug(message)
                return FormValidation(
                    validation=False,
                    error_message=message,
                )

            self.logger.debug("Validation passed")
            return FormValidation(validation=True)
