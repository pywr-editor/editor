from typing import Any

from pywr_editor.form import FloatWidget, FormSection, SlotsTableWidget
from pywr_editor.utils import Logging

from ..node_dialog_form import NodeDialogForm
from .river_split_node_section import RiverSplitSection


class RiverSplitWithGaugeSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a RiverSplitWithGauge node.
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
        return {
            "Configuration": [
                {
                    "name": "mrf",
                    "label": "Minimum residual flow",
                    "field_type": FloatWidget,
                    "field_args": {"min_value": 0},
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
                    "field_type": FloatWidget,
                    "default_value": 0,
                    "value": self.form.get_node_dict_value("mrf_cost"),
                    "help_text": "The cost to associate to the link with the minimum "
                    + "residual flow. Default to 0",
                },
                {
                    "name": "cost",
                    "label": "Other cost",
                    "field_type": FloatWidget,
                    "default_value": 0,
                    "value": self.form.get_node_dict_value("cost"),
                    "help_text": "The cost to associate to the other route. "
                    + "Default to 0",
                },
                {
                    "name": "slots_field",
                    "label": "Slot configuration",
                    "field_type": SlotsTableWidget,
                    "min_value": 1,
                    "validate_fun": RiverSplitSection.check_factors,
                    "value": self.form.node_obj,
                    "help_text": "Provide a name for each node's slot to properly "
                    + "connect the extra slots of this node to the other nodes in "
                    + "the network. You can also define optional factors to set the "
                    + " proportion of the total flow to pass through the additional "
                    + "sub-links",
                },
            ],
        }

    def filter(self, form_data: dict[str, Any]) -> None:
        """
        Unpacks the "slots_field" values and updates the slot names in the edges.
        :param form_data: The form data.
        :return: None
        """
        widget: SlotsTableWidget = self.form.find_field_by_name(
            "slots_field"
        ).widget

        # update slot names in edges
        widget.updated_slot_names_in_edge_helper()
        # unpack values
        widget.unpack_from_data_helper(form_data)

        # remove extra_slots. Pywr set automatically the number using the factors.
        # The form validation forces the factors to match the number of connected nodes.
        del form_data["extra_slots"]

        self.logger.debug(f"Filtered form data to {form_data}")
