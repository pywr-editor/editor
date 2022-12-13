from ..parameter_dialog_form import ParameterDialogForm
from pywr_editor.form import FloatWidget, ParameterLineEditWidget, FormSection
from pywr_editor.utils import Logging


class ScaledProfileParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a ScaledProfileParameter.
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
                    "help_text": "The parameter value to scale",
                },
                {
                    "name": "scale",
                    "field_type": FloatWidget,
                    "default_value": None,
                    "allow_empty": False,
                    "value": self.form.get_param_dict_value("scale"),
                    "help_text": "Scale the parameter value by the provided amount",
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
