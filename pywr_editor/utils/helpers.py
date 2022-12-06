from typing import Any
from pywr_editor.model import ParameterConfig, RecorderConfig


def tooltip_table(comp_obj: ParameterConfig | RecorderConfig):
    """
    Returns the table describing the parameter or recorder configuration in a widget
    tooltip.
    :param comp_obj: The ParameterConfig or RecorderConfig instance.
    :return: The HTML code representing the table.
    """
    table = "<table>"
    for key, value in comp_obj.props.items():
        table += tooltip_table_row(key, value, comp_obj)
    table += "</table>"

    return table


def tooltip_table_row(
    key: str, value: Any, param_obj: ParameterConfig | RecorderConfig | None
) -> str:
    """
    Returns the HTML table row for a widget tooltip.
    :param key: The key.
    :param value: The value.
    :param param_obj: The instance of the parameter.
    :return: The HTML code representing the table row.
    """
    row = ""
    if param_obj is not None:
        humanised_key = f"<i>{param_obj.humanise_attribute_name(key)}</i>"
    else:
        humanised_key = key

    if key == "type":
        row += (
            f"<tr><td colspan='2'><b>{param_obj.humanised_type}</b></td></tr>"
        )
    elif isinstance(value, list):
        if value:
            if all([isinstance(v, (float, int, str)) for v in value]):
                value = list(map(str, value))
                row += (
                    f"<tr><td>{humanised_key}:</td><td style='padding-left:10px'>"
                    + f"{', '.join(value)}</td></tr>"
                )
            else:
                row += f"<tr><td>{humanised_key}:</td><td>"
                row += "<table style='margin-left:10px'>"
                for vi, v in enumerate(value):
                    row += tooltip_table_row(f"#{vi + 1}", v, None)
                row += "</table></td>"

    elif isinstance(value, dict):
        row += f"<tr><td>{humanised_key}:</td><td style='padding-left:10px'>"
        row += "<table style='margin:0'>"
        for sub_key, sub_value in value.items():
            # assume the nested dict is by default a parameter
            if "recorder" in sub_key:
                obj = RecorderConfig(value)
            else:
                obj = ParameterConfig(value)
            row += tooltip_table_row(sub_key, sub_value, obj)
        row += "</table></td>"
    else:
        row += (
            f"<tr><td>{humanised_key}:</td><td style='padding-left:10px'>{value}"
            + "</td></tr>"
        )
    return row
