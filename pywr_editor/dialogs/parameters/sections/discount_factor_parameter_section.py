from ..parameter_dialog_form import ParameterDialogForm
from pywr_editor.form import FloatWidget, FormSection, FormValidation
from pywr_editor.utils import Logging


class DiscountFactorParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a DiscountFactorParameter.
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
                    "name": "discount_rate",
                    "field_type": FloatWidget,
                    "value": self.form.get_param_dict_value("discount_rate"),
                    "allow_empty": False,
                    "validate_fun": self._check_rate,
                    "help_text": "The parameter provides a discount factor for each "
                    "simulated year calculated as the inverse of "
                    "(1+ Discount rate)^(Year - Base year). The rate must be a number"
                    "between 0 and 1",
                },
                {
                    "name": "base_year",
                    "field_type": "integer",
                    "default_value": 0,
                    "value": self.form.get_param_dict_value("base_year"),
                    "allow_empty": False,
                    "help_text": "Base year (i.e. the year with a discount rate "
                    "equal to 1)",
                },
            ],
            "Miscellaneous": [
                {
                    "name": "comment",
                    "value": self.form.get_param_dict_value("comment"),
                },
            ],
        }

        return data_dict

    @staticmethod
    def _check_rate(name: str, label: str, value: int) -> FormValidation:
        """
        Checks that discount rate is between 0 and 1.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        # ignore when value is 0
        if not 0 <= value <= 1:
            return FormValidation(
                validation=False,
                error_message="The number must be between 0 and 1",
            )

        return FormValidation(validation=True)
