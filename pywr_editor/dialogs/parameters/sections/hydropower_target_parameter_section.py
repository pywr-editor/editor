from pywr_editor.form import FloatWidget, FormSection, ParameterLineEditWidget
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class HydropowerTargetParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a HydropowerTargetParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(self.__class__.__name__)

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.form: ParameterDialogForm
        self.logger.debug("Registering form")

        data_dict = {
            "Configuration": [
                {
                    "name": "target",
                    "label": "Production target",
                    "field_type": ParameterLineEditWidget,
                    "value": self.form.get_param_dict_value("target"),
                    "help_text": "Parameter providing the hydropower production "
                    + "target. This can be constant or a time-dependant value with "
                    + "energy per day as unit. The hydropower parameter returns the "
                    + "flow to meet the energy target for a node representing a "
                    + "turbine",
                },
                {
                    "name": "water_elevation_parameter",
                    "label": "Water elevation",
                    "field_type": ParameterLineEditWidget,
                    # optional field
                    "field_args": {"is_mandatory": False},
                    "value": self.form.get_param_dict_value(
                        "water_elevation_parameter"
                    ),
                    "help_text": "Water elevation before the turbine. The working "
                    + "head of the turbine (or potential energy) is the difference "
                    + "between this value and the turbine elevation. If omitted, the "
                    + "working head is simply the turbine elevation",
                },
                {
                    "name": "turbine_elevation",
                    "field_type": FloatWidget,
                    "field_args": {"min_value": 0},
                    "value": self.form.get_param_dict_value(
                        "turbine_elevation"
                    ),
                    "default_value": 0,
                    "help_text": "Elevation of the turbine",
                },
                {
                    "name": "efficiency",
                    "label": "Turbine efficiency",
                    "field_type": FloatWidget,
                    "field_args": {"min_value": 0, "max_value": 1},
                    "value": self.form.get_param_dict_value("efficiency"),
                    "default_value": 1,
                    "help_text": "A number between 0 and 1 to reduced the power "
                    + "generated by the turbine",
                },
                {
                    "name": "density",
                    "label": "Water density",
                    "field_type": FloatWidget,
                    "field_args": {
                        "min_value": 0,
                        "suffix": "kg/m<sup>3</sup>",
                    },
                    "value": self.form.get_param_dict_value("density"),
                    "default_value": 1000,
                    "help_text": "Density of water used in the hydropower equation",
                },
            ],
            "Unit conversion factors": [
                {
                    "name": "flow_unit_conversion",
                    "label": " Flow unit conversion factor",
                    "field_type": FloatWidget,
                    "field_args": {"min_value": 0},
                    "value": self.form.get_param_dict_value(
                        "flow_unit_conversion"
                    ),
                    "default_value": 1,
                    "help_text": "The hydropower equation needs the flow in m<sup>3"
                    + "</sup>/day. Use this conversion factor to convert the flow "
                    + "depending on the units used for the energy target and water "
                    + "head. See the equation in the Pywr manual for more information",
                },
                {
                    "name": "energy_unit_conversion ",
                    "label": " Energy unit conversion factor",
                    "field_type": FloatWidget,
                    "field_args": {"min_value": 0},
                    "value": self.form.get_param_dict_value(
                        "energy_unit_conversion "
                    ),
                    "default_value": pow(10, -6),
                    "help_text": "Convert the power unit used in the hydropower "
                    + "equation. Default to 1e-6 to use MJ/day as input. See the "
                    + "equation in the Pywr manual for more information",
                },
            ],
            "Bounds": [
                {
                    "name": "max_flow",
                    "label": "Maximum flow",
                    "field_type": ParameterLineEditWidget,
                    # optional field
                    "field_args": {"is_mandatory": False},
                    "value": self.form.get_param_dict_value("max_flow"),
                    "help_text": "Limit the parameter flow to the provided amount, "
                    + "if the flow needed to meet the production target is larger",
                },
                {
                    "name": "min_flow",
                    "label": "Minimum flow",
                    "field_type": ParameterLineEditWidget,
                    # optional field
                    "field_args": {"is_mandatory": False},
                    "value": self.form.get_param_dict_value("min_flow"),
                    "help_text": "Always ensure that the parameter flow is at least "
                    + "above the provided amount, if the flow needed to meet the "
                    + "production target is smaller",
                },
                {
                    "name": "min_head",
                    "label": "Minimum head",
                    "field_type": FloatWidget,
                    "field_args": {"min_value": 0},
                    "default_value": 0,
                    "value": self.form.get_param_dict_value("min_head"),
                    "help_text": "Always ensure that the working head (the difference "
                    + "between this value and the turbine elevation) is at least "
                    + "above the provided amount. If not, the hydropower parameter "
                    + "returns no flow",
                },
            ],
            "Miscellaneous": [self.form.comment],
        }

        return data_dict
