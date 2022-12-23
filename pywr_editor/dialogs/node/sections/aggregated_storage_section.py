from pywr_editor.form import FormSection, MultiNodePickerWidget
from pywr_editor.utils import Logging

from ..node_dialog_form import NodeDialogForm


class AggregatedStorageSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a AggregatedStorageSection.
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

        sub_class = "Storage"
        data_dict = {
            "Configuration": [
                {
                    "name": "storage_nodes",
                    "value": self.form.get_node_dict_value("storage_nodes"),
                    "field_type": MultiNodePickerWidget,
                    "field_args": {
                        "include_node_keys": self.form.model_config.pywr_node_data.get_keys_with_parent_class(  # noqa: E501
                            sub_class
                        )
                        + self.form.model_config.includes.get_keys_with_subclass(
                            sub_class, "node"
                        ),
                        "is_mandatory": True,
                    },
                    "help_text": "Combine the absolute storage of the selected nodes",
                },
                self.form.comment,
            ],
        }

        return data_dict
