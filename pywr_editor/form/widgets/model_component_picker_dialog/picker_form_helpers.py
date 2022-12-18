from typing import Literal
from pywr_editor.form import (
    ParameterPickerWidget,
    RecorderPickerWidget,
    ModelComponentSourceSelectorWidget,
    ParameterTypeSelectorWidget,
    RecorderTypeSelectorWidget,
)
from pywr_editor.model import ParameterConfig, RecorderConfig


def build_picker_form_fields(
    component_obj: ParameterConfig | RecorderConfig,
    component_type: Literal["parameter", "recorder"],
    include_comp_key: list[str] | None = None,
) -> dict[str, list[dict]]:
    """
    Returns the dictionary with the fields for the ParameterPickerFormWidget and
    RecorderPickerFormWidget
    :param component_obj: The parameter or recorder instance.
    :param component_type: The component type (parameter or recorder).
    :param include_comp_key: The component keys passed to
    ParameterPickerWidget/RecorderPickerWidget and
    ParameterTypeSelectorWidget/RecorderTypeSelectorWidget.
    :return: The form dictionary with the fields.
    """
    # additional filter to pass to the widgets, if provided
    field_args = None
    if include_comp_key:
        if component_type == "parameter":
            key = "include_param_key"
        elif component_type == "recorder":
            key = "include_recorder_key"
        else:
            raise ValueError(
                "component_type can only be 'parameter; or 'recorder'"
            )

        field_args = {key: include_comp_key}

    # empty dictionary if the component is global so that
    # ParameterTypeSelectorWidget or RecorderTypeSelectorWidget
    # will not load the values stored in the object
    if component_type == "parameter" and component_obj.is_a_model_parameter:
        component_obj.reset_props()
    elif component_type == "recorder" and component_obj.is_a_model_recorder:
        component_obj.reset_props()

    comp_picker_widget = None
    comp_type_selector_widget = None
    if component_type == "parameter":
        comp_picker_widget = ParameterPickerWidget
        comp_type_selector_widget = ParameterTypeSelectorWidget
    elif component_type == "recorder":
        comp_picker_widget = RecorderPickerWidget
        comp_type_selector_widget = RecorderTypeSelectorWidget

    return {
        f"Define {component_type}": [
            {
                "name": "comp_source",
                "label": f"{component_type.title()} source",
                "field_type": ModelComponentSourceSelectorWidget,
                "field_args": {"component_type": component_type},
                "value": component_obj,
            },
            {
                "name": "comp_name",
                "label": f"{component_type.title()} name",
                "field_type": comp_picker_widget,
                "field_args": field_args,
                "value": component_obj.name,
            },
            {
                "name": "type",
                "field_type": comp_type_selector_widget,
                "field_args": field_args,
                "value": component_obj,
            },
        ],
    }
