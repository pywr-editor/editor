from ..parameter_dialog_form import ParameterDialogForm
from pywr_editor.form import FormSection
from pywr_editor.utils import Logging


class UniformDrawdownProfileParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a UniformDrawdownProfileParameter.
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

        return {
            "Configuration": [
                {
                    "name": "reset_day",
                    "field_type": "integer",
                    "min_value": 1,
                    "max_value": 31,
                    "help_text": "The day of the month (1-31) to reset the volume to "
                    + "the initial value",
                    "value": self.form.get_param_dict_value("reset_day"),
                },
                {
                    "name": "reset_month",
                    "field_type": "integer",
                    "min_value": 1,
                    "max_value": 12,
                    "help_text": "The month (1-12) to reset the volume to the initial "
                    + "value",
                    "value": self.form.get_param_dict_value("reset_month"),
                },
                {
                    "name": "residual_days",
                    "field_type": "integer",
                    "default_value": 0,
                    "max_value": 366,
                    "help_text": "The number of days of residual licence to target at "
                    + "the end of the calendar year",
                    "value": self.form.get_param_dict_value("residual_days"),
                },
            ]
        }
