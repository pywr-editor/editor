from typing import Any, Callable, Literal, Type, TypedDict, Union

from PySide6.QtWidgets import QWidget

from .form_custom_widget import FormCustomWidget
from .form_validation import FormValidation


class FieldConfig(TypedDict):
    name: str
    """ the field name """
    label: str
    """ the field label """
    value: Any
    """ the field value. Optional """
    field_type: Union[
        Literal["text", "boolean", "integer"], Type[FormCustomWidget]
    ]
    """ this can be text (for QLineEdit), integer (for SpinBox), boolean (for
    QComboBox with yes/no options) or a callable for a custom FormCustomWidget """
    field_args: dict
    """ additional arguments to pass to custom widgets as dictionary. Optional """
    allow_empty: bool
    """ if False, the form validation fails if the field is empty. Optional """
    hide_label: bool
    """ set to True to hide the label. Default to False, Optional """
    validate_fun: Callable[[str, str, QWidget], FormValidation]
    """ a custom validation function that receives the field name, label, value
     and returns an instance of FormValidation. Optional"""
    default_value: Any
    """ a default value for the field. If the field contains this value when the
    form is saved, the field value is not included in the form values. Optional """
    min_value: int
    """ only available when field_type is integer to limit the QSpinBox values """
    max_value: int
    """ only available when field_type is integer to limit the QSpinBox values """
    suffix: str
    """ only available when field_type is integer to add a suffix to the QSpinBox """
    help_text: str
    """ A string that describes the field """
