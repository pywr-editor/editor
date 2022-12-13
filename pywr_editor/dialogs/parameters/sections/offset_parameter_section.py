from ..parameter_dialog_form import ParameterDialogForm
from pywr_editor.form import ParameterLineEditWidget, FloatWidget, FormSection
from pywr_editor.utils import Logging


"""
 Abstract class for MinParameter, MaxParameter,
 NegativeMinParameter and NegativeMaxParameter.
"""


class OffsetParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for the OffsetParameter.
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
                    "name": "parameter",
                    "field_type": ParameterLineEditWidget,
                    "value": self.form.get_param_dict_value("parameter"),
                    "help_text": "Offset this parameter value by the constant offset "
                    + "provided below",
                },
                {
                    "name": "offset",
                    "field_type": FloatWidget,
                    # pywr class defaults to 0
                    "default_value": 0,
                    "allow_empty": False,
                    "value": self.form.get_param_dict_value("offset"),
                    "help_text": "Apply this offset to the above parameter. "
                    + "Default to 0",
                },
            ],
            self.form.optimisation_config_group_name: [
                self.form.is_variable_field,
                {
                    "name": "lower_bounds",
                    "field_type": FloatWidget,
                    "value": self.form.get_param_dict_value("lower_bounds"),
                    "help_text": "The smallest value for the parameter during "
                    + "optimisation",
                },
                {
                    "name": "upper_bounds",
                    "field_type": FloatWidget,
                    "value": self.form.get_param_dict_value("upper_bounds"),
                    "help_text": "The largest value for the parameter during "
                    + "optimisation",
                },
            ],
        }

        # disable optimisation section
        if self.section_data["enable_optimisation_section"] is False:
            del data_dict[self.form.optimisation_config_group_name]

        return data_dict
