from pywr_editor.form import FormSection, ParameterLineEditWidget
from pywr_editor.utils import Logging

from ..node_dialog_form import NodeDialogForm


class CatchmentSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises a form section for a Catchment node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        self.form = form
        super().__init__(form, section_data)
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
                {
                    "name": "flow",
                    "label": "Maximum flow",
                    "field_type": ParameterLineEditWidget,
                    "field_args": {"is_mandatory": False},
                    "value": self.form.get_node_dict_value("flow"),
                    "help_text": "The inflow from the catchment. Default to 0",
                },
                self.form.cost_field("flow"),
                self.form.comment,
            ],
        }

        return data_dict
