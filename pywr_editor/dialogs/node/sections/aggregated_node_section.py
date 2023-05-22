from pywr_editor.form import (
    FormSection,
    MultiNodePickerWidget,
    TableValuesWidget,
    Validation,
)
from pywr_editor.utils import Logging

from ..node_dialog_form import NodeDialogForm


class AggregatedNodeSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a AggregatedNode.
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
                    "name": "nodes",
                    "value": self.form.get_node_dict_value("nodes"),
                    "field_type": MultiNodePickerWidget,
                    "field_args": {"is_mandatory": True},
                    "help_text": "Combine the flow of the selected nodes",
                },
                {
                    "name": "flow_weights",
                    "value": {
                        "value": self.form.get_node_dict_value("flow_weights"),
                    },
                    "field_type": TableValuesWidget,
                    "field_args": {
                        "show_row_numbers": True,
                        "row_number_label": "Node",
                    },
                    "validate_fun": self.check_weight_size,
                    "help_text": "Scale the flow of each node by provided flow "
                    + "weights",
                },
                self.form.min_flow_field,
                self.form.max_flow_field,
                self.form.comment,
            ],
        }

        return data_dict

    def check_weight_size(
        self, name: str, label: str, value: dict[str, list[int | float]]
    ) -> Validation:
        """
        Checks that, if at least one weight is provided, all the weights
        must be given.
        :param name: The field name.
        :param label: The field label.
        :param value: The list of weights.
        :return:
        """
        nodes = self.form.find_field_by_name("nodes").value()
        if nodes and value["value"] and len(value["value"]) != len(nodes):
            return Validation(
                "When you provide the weight for at least one node, you "
                + "must specify the weights for all the another nodes as well, or "
                + "use 1 not to scale the flow",
            )

        return Validation()

    def filter(self, form_data: dict) -> None:
        """
        Unpacks the flow weights when provided.
        :param form_data: The form data.
        :return: None
        """
        weights = form_data["flow_weights"]["value"]
        if weights:
            form_data["flow_weights"] = weights
        else:
            del form_data["flow_weights"]
