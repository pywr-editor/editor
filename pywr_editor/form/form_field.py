from typing import TYPE_CHECKING, Any, Type

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from pywr_editor.form.widgets.text_widget import TextWidget
from pywr_editor.style import Color
from pywr_editor.utils import Logging

from .form_custom_widget import FormCustomWidget

if TYPE_CHECKING:
    from pywr_editor.form import Form


class FormField(QWidget):
    def __init__(
        self,
        form: "Form",
        name: str,
        label: str,
        field_type: Type[FormCustomWidget] = TextWidget,
        field_args: dict[str, Any] = None,
        value: Any | None = None,
        default_value=None,
        help_text: str | None = None,
    ):
        """
        Initialises a form field.
        :param form: The form instance.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value. Default to TextWidget.
        :param help_text: The help text to add below the field. Default to None.
        :param field_type: A FormCustomWidget type. Default to TextWidget.
        :param field_args: Additional arguments to pass to custom widgets as dictionary.
        Optional.
        """
        super().__init__()
        self.name = name
        self.label = label
        self.form = form
        self.field_type = field_type
        self.default_value = default_value
        self.field_args = field_args

        if field_type is None:
            self.field_type = TextWidget
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
        self.widget = self.field_type(
            name=name, value=value, parent=self, **self.field_args
        )
        # store the default value in the form
        self.form.defaults[name] = self.widget.get_default_value()

        # set properties
        if default_value is None:
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

    def set_warning(self, message: str) -> None:
        """
        Displays a warning message underneath the field and help text.
        :param message: The message to display.
        :return: None
        """
        self.logger.debug(f"WARNING for {self.name}: {message}")
        self._set_message(message, Color("amber", 600), "warning")

    def set_error(self, message: str) -> None:
        """
        Displays am error message underneath the field and help text.
        :param message: The message to display.
        :return: None
        """
        self.logger.debug(f"ERROR for {self.name}: {message}")
        self._set_message(message, Color("red", 700), "error")

    def value(self) -> Any:
        """
        Returns the field value. Widgets must implement the get_value() method.
        :return: The value.
        """
        return self.widget.get_value()
