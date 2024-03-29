from typing import TYPE_CHECKING, Any, Callable

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget

from .validation import Validation

if TYPE_CHECKING:
    from .form import Form, FormField


class FormWidget(QWidget):
    def __init__(
        self,
        name: str,
        value: Any,
        parent: "FormField",
    ):
        """
        Initialises a custom widget.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.name = name
        self.value = value
        self.field = parent
        self.form: "Form" = self.field.form

    def _type(self) -> str:
        """
        Returns the widget type.
        :return: The type
        """
        return self.__class__.__name__

    def get_value(self) -> Any:
        """
        Returns the value set for the widget.
        :return: The widget value.
        """
        raise NotImplementedError(
            f"The value() method is not implemented for {self._type()}"
        )

    def validate(self, name: str, label: str, value: Any) -> Validation:
        """
        Validate the returned value(s) by the widget.
        :param name: The field name.
        :param label: The field label.
        :param value: The file URL.
        :return: The Validation instance.
        """
        return Validation()

    def register_after_render_action(self, action: Callable) -> None:
        """
        Registers an action to execute after the whole form has been rendered and all
        fields are available.
        :return: None.
        """
        self.form.after_render_actions.append(action)

    def get_default_value(self) -> Any:
        """
        Returns the field default value. This is store by FormField in the
        "default_value" property.
        :return: The default value.
        """
        return self.property("default_value")

    @Slot()
    def on_update_value(self) -> None:
        """
        Slots used to update the stored widget value.
        :return: None
        """
        pass

    def after_validate(self, form_dict: dict[str, Any], form_field_name: str) -> None:
        """
        Event executed after the widget is validated and its value is added to the
        the form.
        :param form_dict: The dictionary containing the data of the form the widget is
        child of.
        :param form_field_name: The name of the parent FormField.
        :return: None
        """
        return
