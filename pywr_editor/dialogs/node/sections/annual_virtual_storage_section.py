from ..node_dialog_form import NodeDialogForm
from .abstract_virtual_storage_section import AbstractVirtualStorageSection


class AnnualVirtualStorageSection(AbstractVirtualStorageSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a AnnualVirtualStorage.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            additional_fields=[
                {
                    "name": "reset_day",
                    "label": "Renewal day",
                    "field_type": "integer",
                    "min_value": 1,
                    "max_value": 31,
                    "default_value": 1,
                    "value": form.get_node_dict_value("reset_day"),
                    "help_text": "The day of the month when to reset the storage "
                    + "to its maximum volume. Default to 1",
                },
                {
                    "name": "reset_month",
                    "label": "Renewal month",
                    "field_type": "integer",
                    "min_value": 1,
                    "max_value": 12,
                    "default_value": 1,
                    "value": form.get_node_dict_value("reset_month"),
                    "help_text": "The month when to reset the storage to its maximum "
                    + "volume. Default to 1",
                },
                {
                    "name": "reset_to_initial_volume",
                    "field_type": "boolean",
                    "default_value": False,
                    "value": form.get_node_dict_value(
                        "reset_to_initial_volume"
                    ),
                    "help_text": "Reset the storage to its initial volume instead "
                    + "of its maximum volume each year",
                },
            ],
        )
