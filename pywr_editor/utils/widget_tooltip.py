from dataclasses import dataclass
from typing import Any

from pywr_editor.model import (
    ModelConfig,
    NodeConfig,
    ParameterConfig,
    RecorderConfig,
)


@dataclass
class ModelComponentTooltip:
    model_config: ModelConfig
    """ The model configuration instance """
    comp_obj: ParameterConfig | RecorderConfig | NodeConfig
    """ The model component whose configuration must be shown in the tooltip """

    def __post_init__(self):
        """
        Stores the recorders' keys.
        :return: None
        """
        self.recorder_keys = self.model_config.pywr_recorder_data.keys + list(
            self.model_config.includes.get_custom_recorders().keys()
        )

    def render(self) -> str:
        """
        Returns the table showing the configuration of a parameter, recorder or node in
        a widget tooltip.
        :return: The HTML code representing the table.
        """
        table = "<table>"
        table += self.title_row(self.comp_obj)
        for key, value in self.comp_obj.props.items():
            table += self.table_row(key, value, self.comp_obj)
        table += "</table>"

        return table

    @staticmethod
    def title_row(
        comp_obj: ParameterConfig | RecorderConfig | NodeConfig,
    ) -> str:
        """
        Returns the row with the tooltip section title.
        :param comp_obj: The ParameterConfig, RecorderConfig or NodeConfig instance.
        :return: The HTML code representing the row.
        """
        if comp_obj is None or comp_obj.props is None:
            return ""

        row = "<tr><td colspan='2'>"
        if isinstance(comp_obj, NodeConfig):
            row += f"<b style='font-size:12pt'>{comp_obj.name} "
            row += f"({comp_obj.humanised_type}) </b>"
        else:
            row += f"<b>{comp_obj.humanised_type}</b>"
        row += "</td></tr>"
        return row

    def table_row(
        self,
        key: str,
        value: Any,
        comp_obj: ParameterConfig | RecorderConfig | NodeConfig | None,
    ) -> str:
        """
        Returns the HTML table row for a widget tooltip.
        :param key: The key.
        :param value: The value.
        :param comp_obj: The ParameterConfig, RecorderConfig or NodeConfig instance.
        Default to None.
        :return: The HTML code representing the table row.
        """
        keys_to_skip = ["position", "type", "color"]
        if key in keys_to_skip or (
            isinstance(comp_obj, NodeConfig) and key == "name"
        ):
            return ""

        row = ""
        if comp_obj is not None:
            humanised_key = f"<i>{comp_obj.humanise_attribute_name(key)}</i>"
        else:
            humanised_key = key

        if isinstance(value, list):
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
                        row += self.table_row(f"#{vi + 1}", v, None)
                    row += "</table></td>"

        elif isinstance(value, dict):
            row += (
                f"<tr><td>{humanised_key}:</td><td style='padding-left:10px'>"
            )
            row += "<table style='margin:0'>"

            # show type
            obj = None  # dictionary may not be a model component
            if "type" in value:
                # default to parameter
                if value["type"] in self.recorder_keys:
                    obj = RecorderConfig(value)
                else:
                    obj = ParameterConfig(value)

            row += self.title_row(obj)
            for sub_key, sub_value in value.items():
                if sub_key in keys_to_skip:
                    continue
                row += self.table_row(sub_key, sub_value, obj)
            row += "</table></td>"
        else:
            row += (
                f"<tr><td>{humanised_key}:</td><td style='padding-left:10px'>{value}"
                + "</td></tr>"
            )
        return row
