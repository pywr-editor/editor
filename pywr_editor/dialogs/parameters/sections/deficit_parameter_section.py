from ..parameter_dialog_form import ParameterDialogForm
from pywr_editor.form import NodePickerWidget, FormSection
from pywr_editor.utils import Logging


class DeficitParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a DeficitParameter.
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
                    "name": "node",
                    "field_type": NodePickerWidget,
                    "value": self.form.get_param_dict_value("node"),
                    "allow_empty": False,
                    "help_text": "The parameter provides the flow deficit for the "
                    + "specified node above",
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
