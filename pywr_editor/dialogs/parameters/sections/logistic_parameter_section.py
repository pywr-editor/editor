from pywr_editor.form import FloatWidget, FormSection
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class LogisticParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a LogisticParameter.
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
                    "name": "value",
                    "label": "Reference value",
                    "field_type": FloatWidget,
                    "default_value": 0,
                    "value": self.form.get_param_dict_value("value"),
                    "allow_empty": False,
                    "help_text": "This parameter returns an output between based on "
                    + "the following logistic function: Max output / (1 + Exp(-Growth "
                    + "rate*Reference value)). Max output is returned when the "
                    + "function value is at its upper bound. Default to 0",
                },
                {
                    "name": "max_output",
                    "label": "Maximum output",
                    "field_type": FloatWidget,
                    "default_value": 1,
                    "value": self.form.get_param_dict_value("max_output"),
                    "allow_empty": False,
                    "help_text": "The maximum output returned by the parameter. "
                    + "Default to 1",
                },
                {
                    "name": "growth_rate",
                    "field_type": FloatWidget,
                    "default_value": 1,
                    "value": self.form.get_param_dict_value("growth_rate"),
                    "allow_empty": False,
                    "help_text": "The growth rate of the logistic function. "
                    + "Default to 1",
                },
            ],
            self.form.optimisation_config_group_name: [
                self.form.is_variable_field,
                {
                    "name": "lower_bounds",
                    "label": "Lower bound",
                    "field_type": FloatWidget,
                    "default_value": -6,
                    "value": self.form.get_param_dict_value("lower_bounds"),
                    "allow_empty": False,
                    "help_text": "The smallest value during optimisation. "
                    + "Default to -6",
                },
                {
                    "name": "upper_bounds",
                    "label": "Upper bound",
                    "field_type": FloatWidget,
                    "default_value": 6,
                    "value": self.form.get_param_dict_value("upper_bounds"),
                    "allow_empty": False,
                    "help_text": "The largest value during optimisation. "
                    + "Default to 6",
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
