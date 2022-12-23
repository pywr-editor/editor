from pywr_editor.form import ParameterLineEditWidget
from pywr_editor.utils import Logging

from ..node_dialog_form import NodeDialogForm
from .abstract_storage_section import AbstractStorageSection

"""
 Section for a Storage node. NOTE: the num_inputs
 and num_outputs property are mentioned in the manual,
 but are not used anywhere in the code. Therefore,
 they are not included in this section.
"""


class StorageSection(AbstractStorageSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a Storage.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form = form
        self.logger = Logging().logger(self.__class__.__name__)

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.logger.debug("Registering form")

        data_dict = {
            "Configuration": [
                self.form.cost_field("storage"),
                {
                    "name": "min_volume",
                    "label": "Minimum storage",
                    "value": self.form.get_node_dict_value("min_volume"),
                    "field_type": ParameterLineEditWidget,
                    "field_args": {
                        "is_mandatory": False,
                    },
                    "default_value": 0,
                    "help_text": "The minimum volume of the storage. Default to 0",
                },
                {
                    "name": "max_volume",
                    "label": "Maximum storage",
                    "value": self.form.get_node_dict_value("max_volume"),
                    "field_type": ParameterLineEditWidget,
                    "field_args": {
                        "is_mandatory": False,
                    },
                    "help_text": "The maximum volume of the storage. Default to 0",
                },
                self.form.initial_volume_field,
                self.form.initial_volume_pc_field,
            ],
            "Level data": [
                {
                    "name": "level",
                    "value": self.form.get_node_dict_value("level"),
                    "field_type": ParameterLineEditWidget,
                    "field_args": {
                        "is_mandatory": False,
                    },
                    "help_text": "A parameter providing the storage level. Optional",
                },
                {
                    "name": "area",
                    "value": self.form.get_node_dict_value("area"),
                    "field_type": ParameterLineEditWidget,
                    "field_args": {
                        "is_mandatory": False,
                    },
                    "help_text": "A parameter providing the storage surface area. "
                    + "Optional",
                },
            ],
            "Miscellaneous": [
                self.form.comment,
            ],
        }
        return data_dict
