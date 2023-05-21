from pywr_editor.form import FormSection, StoragePickerWidget
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class StorageParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a StorageParameter.
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
                    "name": "storage_node",
                    "field_type": StoragePickerWidget,
                    "value": self.form.get_param_dict_value("storage_node"),
                    "help_text": "This parameter returns the storage from the "
                    "node specified above",
                },
                {
                    "name": "use_proportional_volume",
                    "field_type": "boolean",
                    "default_value": False,
                    "value": self.form.get_param_dict_value("use_proportional_volume"),
                    "help_text": "If Yes the storage is returned as proportional "
                    "volume (between 0 and 1)",
                },
            ],
            "Miscellaneous": [self.form.comment],
        }

        return data_dict
