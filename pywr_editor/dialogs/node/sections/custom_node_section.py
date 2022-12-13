from typing import Any, TYPE_CHECKING
from pywr_editor.form import FormSection, DictionaryWidget
from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from ..node_dialog_form import NodeDialogForm

"""
 This section allows setting up a custom node dictionary
 by providing key/value pairs.
"""


class CustomNodeSection(FormSection):
    def __init__(self, form: "NodeDialogForm", section_data: dict):
        """
        Initialises the form section for a custom node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form=form, section_data=section_data)
        self.form = form
        self.logger = Logging().logger(self.__class__.__name__)

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.logger.debug("Registering form")

        # remove type and name for DictionaryWidget
        data_dict = {
            "Configuration": [
                {
                    "name": "component_dict",
                    "label": "Dictionary",
                    "field_type": DictionaryWidget,
                    "value": self.form.node_dict.copy(),
                    "help_text": "Configure the node by providing its dictionary "
                    + "keys and values",
                },
                {
                    "name": "comment",
                    "value": self.form.get_node_dict_value("comment"),
                },
            ],
        }

        return data_dict

    def filter(self, form_data: dict[str, Any]) -> None:
        """
        Set the component type.
        :param form_data: The form data dictionary.
        :return: None.
        """
        # unpack the dictionary items
        for key, value in form_data["component_dict"].items():
            form_data[key] = value
        del form_data["component_dict"]
