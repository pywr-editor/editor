from pywr_editor.form import (
    FloatWidget,
    NodePickerWidget,
    ParameterLineEditWidget,
)

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class AbstractHydropowerRecorderSection(AbstractRecorderSection):
    def __init__(
        self,
        form: RecorderDialogForm,
        section_data: dict,
        node_help_text: str,
        log_name: str,
    ):
        """
        Initialises the form section for hydropower recorders.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param node_help_text: The help text for the "node" field.
        :param log_name: The log name.
        """
        fields = [
            {
                "name": "node",
                "field_type": NodePickerWidget,
                "value": form.get_recorder_dict_value("node"),
                "help_text": node_help_text,
            },
            {
                "name": "water_elevation_parameter",
                "label": "Water elevation",
                "field_type": ParameterLineEditWidget,
                # optional field
                "field_args": {"is_mandatory": False},
                "value": form.get_recorder_dict_value(
                    "water_elevation_parameter"
                ),
                "help_text": "Water elevation before the turbine. The working head of "
                + "the turbine (or potential energy) is the difference between this "
                + "value and the turbine elevation. If omitted, the working "
                + "head is simply the turbine elevation",
            },
            {
                "name": "turbine_elevation",
                "field_type": FloatWidget,
                "field_args": {"min_value": 0},
                "value": form.get_recorder_dict_value("turbine_elevation"),
                "default_value": 0,
                "help_text": "Elevation of the turbine",
            },
            {
                "name": "efficiency",
                "label": "Turbine efficiency",
                "field_type": FloatWidget,
                "field_args": {"min_value": 0, "max_value": 1},
                "value": form.get_recorder_dict_value("efficiency"),
                "default_value": 1,
                "help_text": "A number between 0 and 1 to reduced the power generated "
                + "by the turbine",
            },
            {
                "name": "density",
                "label": "Water density",
                "field_type": FloatWidget,
                "field_args": {"min_value": 0, "suffix": "m<sup>2</sup>"},
                "value": form.get_recorder_dict_value("density"),
                "default_value": 1000,
                "help_text": "Density of water used in the hydropower equation",
            },
        ]
        additional_sections = {
            "Unit conversion factors": [
                {
                    "name": "flow_unit_conversion",
                    "label": " Flow unit conversion factor",
                    "field_type": FloatWidget,
                    "field_args": {"min_value": 0},
                    "value": form.get_recorder_dict_value(
                        "flow_unit_conversion"
                    ),
                    "default_value": 1,
                    "help_text": "The hydropower equation needs the flow in "
                    + "m<sup>3</sup>/day. Use this conversion  factor to convert the "
                    + "flow depending on the units used for the energy target and "
                    + "water head. See the equation in the Pywr manual for more "
                    + "information",
                },
                {
                    "name": "energy_unit_conversion ",
                    "label": " Energy unit conversion factor",
                    "field_type": FloatWidget,
                    "field_args": {"min_value": 0},
                    "value": form.get_recorder_dict_value(
                        "energy_unit_conversion "
                    ),
                    "default_value": pow(10, -6),
                    "help_text": "Convert the power unit used in the hydropower "
                    + "equation. Default to 1e-6 to use MJ /day as input. See the "
                    + "equation in the Pywr manual for more information",
                },
            ],
        }
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            additional_sections=additional_sections,
            log_name=log_name,
        )
