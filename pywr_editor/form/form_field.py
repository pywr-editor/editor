from typing import TYPE_CHECKING, Any, Literal, Type, Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QLineEdit, QSizePolicy, QVBoxLayout, QWidget

from pywr_editor.style import Color
from pywr_editor.utils import Logging
from pywr_editor.widgets import SpinBox, ToggleSwitchWidget

from .form_custom_widget import FormCustomWidget

if TYPE_CHECKING:
    from pywr_editor.form import Form


class FormField(QWidget):
    def __init__(
        self,
        form: "Form",
        name: str,
        label: str,
        field_type: Type[FormCustomWidget]
        | Literal["text", "boolean", "integer"] = "text",
        field_args: dict[str, Any] = None,
        value: str | bool | int | float | None = None,
        default_value=None,
        help_text: str | None = None,
        min_value: int | None = None,
        max_value: int | None = None,
        suffix: str | None = None,
    ):
        """
        Initialises a form field.
        :param form: The form instance.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value. Default to None.
        :param help_text: The help text to add below the field. Default to None.
        :param field_type: The field type (text, integer, boolean or a widget
        inheriting from FormCustomWidget). Default to "text".
        :param field_args: Additional arguments to pass to custom widgets as
        dictionary. Optional.
        :param default_value: The default value for the field. Optional.
        :param min_value: The minimum value to use when field_type is integer. Optional
        :param max_value: The maximum value to use when field_type is integer. Optional
        :param suffix: The suffix to use when field_type is integer. Optional.
        """
        super().__init__()
        self.name = name
        self.label = label
        self.form = form
        self.field_type = field_type
        self.default_value = default_value
        if field_type is None:
            self.field_type = "text"
        self.field_args = field_args
        if field_args is None:
            self.field_args = {}

        self.logger = Logging().logger(self.__class__.__name__)
        if isinstance(self.field_type, str):
            log_type = self.field_type
        else:
            log_type = self.field_type.__name__
        self.logger.debug(f"Loading field {log_type}({name})")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(3)
        self.setObjectName(name)

        # message
        self.message = QLabel()
        self.message.setWordWrap(True)
        self.message.base_style = "font-size:12px;"
        self.message.setStyleSheet(self.message.base_style)
        self.message.hide()

        # field
        self.widget: Union[
            FormCustomWidget, QLineEdit, SpinBox, ToggleSwitchWidget, None
        ] = None
        warning_message = None
        # custom widget
        if self.is_custom_widget:
            self.widget = self.field_type(
                name=name, value=value, parent=self, **self.field_args
            )
            # store the default value in the form
            self.form.defaults[name] = self.widget.get_default_value()

        # QLine edit
        elif self.field_type == "text":
            self.widget = QLineEdit()

            if value is not None:
                self.widget.setText(str(value))
            elif default_value is not None:
                self.widget.setText(str(default_value))
            else:
                self.widget.setText("")
        # QSpinBox
        elif self.field_type == "integer":
            self.widget = SpinBox()
            self.widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)

            # noinspection PyTypeChecker
            if min_value is not None and isinstance(min_value, int):
                self.widget.setMinimum(min_value)
            if max_value is not None and isinstance(max_value, int):
                self.widget.setMaximum(max_value)
            if suffix is not None and isinstance(suffix, str):
                self.widget.setSuffix(f" {suffix}")

            if value is not None and isinstance(value, int):
                if min_value and value < min_value:
                    warning_message = f"The provided value ({value}) must be "
                    warning_message += f"larger than the minimum ({min_value})"
                elif max_value and value > max_value:
                    warning_message = f"The provided value ({value}) must be "
                    warning_message += f"smaller than the maximum ({max_value})"
                self.widget.setValue(value)
            elif default_value is not None and isinstance(default_value, int):
                self.widget.setValue(default_value)
            elif min_value is not None:
                self.widget.setValue(min_value)

        # ToggleSwitchWidget with boolean
        elif self.field_type == "boolean":
            self.widget = ToggleSwitchWidget()
            self.widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)

            if default_value is not None and not isinstance(default_value, bool):
                raise ValueError(f"default_value for '{name}' must be a boolean")
            if value is None or not isinstance(value, bool):  # use the default value
                self.widget.setChecked(True if default_value else False)
            else:
                self.widget.setChecked(value)
        else:
            raise NameError(
                "The field type can only be text, integer, boolean or a "
                + f"FormCustomWidget instance. {self.field_type} given"
            )

        # set properties
        if self.is_custom_widget and default_value is None:
            # prioritise value in dict than custom widget
            default_value = self.widget.get_default_value()
        # noinspection PyTypeChecker
        self.widget.setProperty("default_value", default_value)
        self.widget.setObjectName(name)

        # help text
        self.help_text = None
        if help_text is not None:
            self.help_text = QLabel(help_text)
            self.help_text.setWordWrap(True)
            self.help_text.setStyleSheet(
                f"font-size:12px;color: {Color('gray', 500).hex}"
            )

        # populate the layout
        layout.addWidget(self.widget)
        layout.setAlignment(self.widget, Qt.AlignTop)
        layout.addWidget(self.message)

        if self.help_text is not None:
            layout.addWidget(self.help_text)
        # set error message for built-in field types
        if warning_message:
            self.set_warning_message(warning_message)

    @property
    def is_custom_widget(self) -> bool:
        """
        Checks if the field type is a custom widget.
        :return: True if the field type is a custom widget, False otherwise.
        """
        # noinspection PyTypeChecker
        return callable(self.field_type) and issubclass(
            self.field_type, FormCustomWidget
        )

    def clear_message(self, message_type: str | None = None) -> None:
        """
        Clears any error or warning messages set on the form field.
        :param message_type: Clear the message only if of the given type.
        :return: None
        """
        self.logger.debug(
            f"Clearing message for {self.name}; filtering type {message_type}"
        )
        # noinspection PyTypeChecker
        if (
            message_type is None
            or self.message.property("message_type") == message_type
        ):
            self.message.setText("")
            self.message.hide()

    def _set_message(
        self, message: str | None, color: Color, message_type: str
    ) -> None:
        """
        Displays a warning message underneath the field and help text.
        :param message: The message to display.
        :param color: The message color to use for the text and icon.
        :param message_type: A string indicating the type of message.
        :return: None
        """
        if message == "" or message is None:
            return
        self.message.setText(message)
        # noinspection PyTypeChecker
        self.message.setProperty("message_type", message_type)
        self.message.setStyleSheet(f"{self.message.styleSheet()}; color: {color.hex};")
        # if a message is set before the field is assigned to a parent,
        # do not show the message otherwise a floating window will apper
        # temporarily
        if self.parent():
            self.message.show()

    def set_warning_message(self, message: str) -> None:
        """
        Displays a warning message underneath the field and help text.
        :param message: The message to display.
        :return: None
        """
        self._set_message(message, Color("amber", 600), "warning")

    def set_error_message(self, message: str) -> None:
        """
        Displays am error message underneath the field and help text.
        :param message: The message to display.
        :return: None
        """
        self._set_message(message, Color("red", 700), "error")

    def value(self) -> Any:
        """
        Returns the field value. Custom widgets must implement the get_value() method.
        :return: The value.
        """
        # noinspection PyTypeChecker
        default_value = self.widget.property("default_value")
        if self.is_custom_widget:
            self.widget: FormCustomWidget
            return self.widget.get_value()
        elif self.field_type == "text":
            self.widget: QLineEdit
            value = self.widget.text()
            if value == "" and default_value is not None:
                return default_value
            return value
        elif self.field_type == "integer":
            self.widget: SpinBox
            return self.widget.value()
        elif self.field_type == "boolean":
            return self.widget.isChecked()
        else:
            raise NameError(
                "The field type can only be text, integer, boolean or a "
                + f"FormCustomWidget instance. {self.field_type} given."
            )
