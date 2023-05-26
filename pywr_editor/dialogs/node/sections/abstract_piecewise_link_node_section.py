from typing import TYPE_CHECKING

from pywr_editor.form import FormSection, FormValidation, ParametersListPickerWidget
from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from ..node_dialog_form import NodeDialogForm


class AbstractPiecewiseLinkNodeSection(FormSection):
    def __init__(
        self,
        form: "NodeDialogForm",
        section_data: dict,
        log_name: str,
        additional_fields: list[dict] | None = None,
    ):
        """
        Initialises a general form section for a PiecewiseLink node or nodes inheriting
        from it.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param log_name: The log name.
        :param additional_fields: Additional fields to add to the abstract section.
        """
        super().__init__(form, section_data)
        self.form = form
        self.logger = Logging().logger(log_name)
        if additional_fields:
            self.additional_fields = additional_fields
        else:
            self.additional_fields = []

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
                    "name": "nsteps",
                    "label": "Number of sub links",
                    "field_type": "integer",
                    "min_value": 1,
                    "value": self.form.get_node_dict_value("nsteps"),
                    "help_text": "The number of sub-links to create within the node. "
                    + "A cost and a maximum flow can be set on each link",
                },
                # cost and max flow values can be set to null in the list. This is
                # not supported by the widget, but the user can set the cost and
                # max_flow default values of the Node component
                {
                    "name": "max_flows",
                    "label": "Maximum flows",
                    "field_type": ParametersListPickerWidget,
                    "field_args": {"is_mandatory": False},
                    "validate_fun": self.check_size,
                    "value": self.form.get_node_dict_value("max_flows"),
                    "help_text": "A monotonic increasing list of maximum flows",
                },
                {
                    "name": "costs",
                    "field_type": ParametersListPickerWidget,
                    "field_args": {"is_mandatory": False},
                    "validate_fun": self.check_size,
                    "value": self.form.get_node_dict_value("costs"),
                    "help_text": "A list of costs corresponding to the 'Maximum flows'",
                },
            ]
            + self.additional_fields,
            "Miscellaneous": [
                self.form.comment,
            ],
        }

        return data_dict

    def check_size(
        self, name: str, label: str, value: list[str, dict, int, float]
    ) -> FormValidation:
        """
        Checks that the number of values in "max_flow" and "cost" matches "nsteps".
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The form validation instance.
        """
        nsteps = self.form.find_field_by_name("nsteps").value()
        if value and len(value) != nsteps:
            return FormValidation(
                validation=False,
                error_message=f"The number of values ({len(value)}) must "
                + f"match the number of sub-links ({nsteps})",
            )
        return FormValidation(validation=True)
