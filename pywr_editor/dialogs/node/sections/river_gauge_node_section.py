from pywr_editor.form import FormSection, ParameterLineEditWidget
from pywr_editor.utils import Logging

from ..node_dialog_form import NodeDialogForm


class RiverGaugeSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a RiverGaugeNode node.
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
                {
                    "name": "mrf",
                    "label": "Minimum residual flow",
                    "field_type": ParameterLineEditWidget,
                    "default_value": 0,
                    "value": self.form.get_node_dict_value("mrf"),
                    "help_text": "The minimum residual flow (MRF) to maintain at the "
                    + "gauge. Default to 0. The node internally creates two sub "
                    + "links one, where the MRF is routed with the MRF cost provided "
                    + "below, and one where the remainder of the flow goes to",
                },
                {
                    "name": "mrf_cost",
                    "label": "Minimum residual flow cost",
                    "field_type": ParameterLineEditWidget,
                    "default_value": 0,
                    "value": self.form.get_node_dict_value("mrf_cost"),
                    "help_text": "The cost to associate to the link with the minimum "
                    + "residual flow. Default to 0",
                },
                {
                    "name": "cost",
                    "label": "Other cost",
                    "field_type": ParameterLineEditWidget,
                    "default_value": 0,
                    "value": self.form.get_node_dict_value("cost"),
                    "help_text": "The cost to associate to the other route. "
                    + "Default to 0",
                },
                self.form.comment,
            ],
        }

        return data_dict
