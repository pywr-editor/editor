from typing import Any, Callable, NotRequired, Type, TypedDict

from .form_widget import FormWidget
from .validation import Validation


class FieldConfig(TypedDict):
    name: str
    """ the field name """
    value: Any
    """ the field value """
    label: NotRequired[str]
    """ the field label """
    field_type: NotRequired[Type[FormWidget]]
    """ A class of type FormCustomWidget containing the widget """
    field_args: NotRequired[dict]
    """ additional arguments to pass to custom widgets as dictionary. Optional """
    allow_empty: NotRequired[bool]
    """ if False, the form validation fails if the field is empty. Optional """
    hide_label: NotRequired[bool]
    """ set to True to hide the label. Default to False """
    validate_fun: NotRequired[Callable[[str, str, Any], Validation]]
    """ a custom validation function that receives the field name, label, value
     and returns an instance of Validation. Optional"""
    default_value: NotRequired[Any]
    """ a default value for the field. If the field contains this value when the
    form is saved, the field value is not included in the form values. Optional """
    min_value: NotRequired[int]
    """ only available when field_type is integer to limit the QSpinBox values """
    max_value: NotRequired[int]
    """ only available when field_type is integer to limit the QSpinBox values """
    suffix: NotRequired[str]
    """ only available when field_type is integer to add a suffix to the QSpinBox """
    help_text: NotRequired[str]
    """ A string that describes the field """
