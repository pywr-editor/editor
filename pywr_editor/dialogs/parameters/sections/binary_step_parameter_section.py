from pywr_editor.form import FloatWidget, FormSection
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class BinaryStepParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a BinaryStepParameter.
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
                    "help_text": "This parameter returns the output below when the "
                    + "reference value provided above is positive, zero otherwise. "
                    + "This parameter is meant to be used in optimisation problems. "
                    + "Default to 0",
                },
                {
                    "name": "output",
                    "field_type": FloatWidget,
                    "default_value": 1,
                    "value": self.form.get_param_dict_value("output"),
                    "allow_empty": False,
                    "help_text": "The output returned by the parameter when Reference "
                    + "value is positive. Default to 1",
                },
            ],
            self.form.optimisation_config_group_name: [
                self.form.is_variable_field,
                {
                    "name": "lower_bounds",
                    "label": "Lower bound",
                    "field_type": FloatWidget,
                    "default_value": -1,
                    "value": self.form.get_param_dict_value("lower_bounds"),
                    "allow_empty": False,
                    "help_text": "The smallest value during optimisation. "
                    + "Default to -1",
                },
                {
                    "name": "upper_bounds",
                    "label": "Upper bound",
                    "field_type": FloatWidget,
                    "default_value": 1,
                    "value": self.form.get_param_dict_value("upper_bounds"),
                    "allow_empty": False,
                    "help_text": "The largest value during optimisation. "
                    + "Default to 1",
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
