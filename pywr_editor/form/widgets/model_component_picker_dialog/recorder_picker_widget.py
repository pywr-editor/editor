from typing import TYPE_CHECKING, Union

from pywr_editor.form import (
    FormField,
    FormValidation,
    ModelRecorderPickerWidget,
    ParameterPickerWidget,
)

if TYPE_CHECKING:
    from pywr_editor.form import ParameterPickerFormWidget, RecorderPickerFormWidget

"""
 This widgets inherits from ModelRecorderPickerWidget but
 with a different validation method and is used by the
 RecorderPickerFormWidget
"""


class RecorderPickerWidget(ModelRecorderPickerWidget):
    def __init__(self, name: str, value: str | None, parent: FormField, **kwargs):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected recorder name.
        :param parent: The parent widget.
        """
        super().__init__(name, value, parent, **kwargs)

    def validate(self, name: str, label: str, value: str) -> FormValidation:
        """
        Validates the value. The name is mandatory only if the value of
        ModelComponentSelectorWidget is set to "model_component".
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The instance of FormValidation
        """
        self.form: Union["ParameterPickerFormWidget", "RecorderPickerFormWidget"]
        return ParameterPickerWidget.validate_model_component(value, self.form)
