from typing import Any

from pywr_editor.form import FieldConfig, SlotsTableWidget
from pywr_editor.utils import Logging

from ..node_dialog_form import NodeDialogForm
from .abstract_piecewise_link_node_section import AbstractPiecewiseLinkNodeSection


class MultiSplitLinkSection(AbstractPiecewiseLinkNodeSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a MultiSplitLink node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)

        super().__init__(
            form,
            section_data,
            additional_fields=[
                FieldConfig(
                    name="slots_field",
                    label="Slot configuration",
                    field_type=SlotsTableWidget,
                    min_value=1,
                    value=form.node_obj,
                    help_text="Provide a name for each node's slot to properly "
                    "connect the extra slots of this node to the other nodes in "
                    "the network. You can also define optional factors to set the "
                    " proportion of the total flow to pass through the additional "
                    "sub-links",
                ),
            ],
        )

    def filter(self, form_data: dict[str, Any]) -> None:
        """
        Unpacks the "slots_field" values and updates the slot names in the edges.
        :param form_data: The form data.
        :return: None
        """
        widget: SlotsTableWidget = self.form.find_field("slots_field").widget

        # update slot names in edges
        widget.updated_slot_names_in_edge_helper()
        # unpack values
        widget.unpack_from_data_helper(form_data)

        self.logger.debug(f"Filtered form data to {form_data}")
