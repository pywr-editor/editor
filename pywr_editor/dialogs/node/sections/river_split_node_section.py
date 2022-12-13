from typing import Any
from ..node_dialog_form import NodeDialogForm
from pywr_editor.form import FormSection, SlotsTableWidget, FormValidation
from pywr_editor.utils import Logging

"""
 The node sets defaults value for the "nsteps", "max_flows"
 and "costs" parameters. In theory these can be changed, based
 on the node implementation, but this would convert the node
 to a MultiSplitLink and therefore the fields for these
 properties are added to the form.
"""


class RiverSplitSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a RiverSplit node.
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
                    "name": "slots_field",
                    "label": "Slot configuration",
                    "field_type": SlotsTableWidget,
                    "min_value": 1,
                    "validate_fun": self.check_factors,
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
        # The form validation forces the factors to match the number of connected
        # nodes.
        del form_data["extra_slots"]

        self.logger.debug(f"Filtered form data to {form_data}")

    @staticmethod
    def check_factors(
        name: str, label: str, value: dict[str, Any]
    ) -> FormValidation:
        """
        Checks that all the factors are provided.
        :param name: The field name.
        :param label: The field label.
        :param value: The list of factors.
        :return: The form validation.
        """
        if value["factors"] is None or any(
            [f is None for f in value["factors"]]
        ):
            return FormValidation(
                validation=False, error_message="All the factors are mandatory"
            )

        return FormValidation(validation=True)
