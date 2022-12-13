from math import pi
from ..parameter_dialog_form import ParameterDialogForm
from pywr_editor.form import FloatWidget, FormSection, TableValuesWidget
from pywr_editor.utils import Logging


class AnnualHarmonicSeriesParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a AnnualHarmonicSeriesParameter.
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
                    "name": "mean",
                    "field_type": FloatWidget,
                    "value": self.form.get_param_dict_value("mean"),
                    "allow_empty": False,
                    "help_text": "The mean value of the series corresponding to the "
                    "zeroth harmonic",
                },
                {
                    "name": "amplitudes_phases",
                    "field_type": TableValuesWidget,
                    "value": {
                        "amplitudes": self.form.get_param_dict_value(
                            "amplitudes"
                        ),
                        "phases": self.form.get_param_dict_value("phases"),
                    },
                    "field_args": {
                        "min_total_values": 1,
                        "scientific_notation": True,
                    },
                    "help_text": "A list of amplitudes and phases to use for the "
                    + "harmonic cosine functions",
                },
            ],
            self.form.optimisation_config_group_name: [
                self.form.is_variable_field,
                {
                    "name": "mean_lower_bounds",
                    "field_type": FloatWidget,
                    "value": self.form.get_param_dict_value(
                        "mean_lower_bounds"
                    ),
                    "help_text": "The lower bound for the mean during optimisation",
                },
                {
                    "name": "mean_upper_bounds",
                    "field_type": FloatWidget,
                    "value": self.form.get_param_dict_value(
                        "mean_upper_bounds"
                    ),
                    "help_text": "The upper bound for the mean during optimisation",
                },
                {
                    "name": "amplitude_lower_bounds",
                    "field_type": FloatWidget,
                    "value": self.form.get_param_dict_value(
                        "amplitude_lower_bounds"
                    ),
                    "help_text": "The lower bound for the amplitude during "
                    + "optimisation. The constrain is the same for all harmonic "
                    + "cosine function",
                },
                {
                    "name": "amplitude_upper_bounds",
                    "field_type": FloatWidget,
                    "value": self.form.get_param_dict_value(
                        "amplitude_upper_bounds"
                    ),
                    "help_text": "The upper bound for the amplitude during "
                    + "optimisation. The constrain is the same for all harmonic "
                    + "cosine function",
                },
                {
                    "name": "phase_lower_bounds",
                    "field_type": FloatWidget,
                    "value": self.form.get_param_dict_value(
                        "phase_lower_bounds"
                    ),
                    "help_text": "The lower bound for the phase during optimisation. "
                    "The constrain is the same for all harmonic cosine function",
                },
                {
                    "name": "phase_upper_bounds",
                    "field_type": FloatWidget,
                    "field_args": {"max_value": 2 * pi},
                    "value": self.form.get_param_dict_value(
                        "phase_upper_bounds"
                    ),
                    "help_text": "The upper bound for the phase during optimisation. "
                    "The constrain is the same for all harmonic cosine function",
                },
            ],
            "Miscellaneous": [
                {
                    "name": "comment",
                    "value": self.form.get_param_dict_value("comment"),
                },
            ],
        }

        # disable optimisation section
        if self.section_data["enable_optimisation_section"] is False:
            del data_dict[self.form.optimisation_config_group_name]

        return data_dict

    def filter(self, form_data):
        """
        Unpacks the "amplitudes_phases" field.
        :param form_data: The form data.
        :return: None
        """
        # field is mandatory
        for var_name, var_values in form_data["amplitudes_phases"].items():
            form_data[var_name] = var_values
        del form_data["amplitudes_phases"]
