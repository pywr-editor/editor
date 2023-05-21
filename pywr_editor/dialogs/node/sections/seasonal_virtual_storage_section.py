from ..node_dialog_form import NodeDialogForm
from .abstract_virtual_storage_section import AbstractVirtualStorageSection


class SeasonalVirtualStorageSection(AbstractVirtualStorageSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a SeasonalVirtualStorage.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        form: NodeDialogForm

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
                    "help_text": "The day of the month when the storage starts to be "
                    + "calculated and is reset to its maximum volume. Default to 1",
                },
                {
                    "name": "reset_month",
                    "label": "Renewal month",
                    "field_type": "integer",
                    "min_value": 1,
                    "max_value": 12,
                    "default_value": 1,
                    "value": form.get_node_dict_value("reset_month"),
                    "help_text": "The month when the storage starts to be calculated "
                    + "and is reset to its maximum volume. Default to 1",
                },
                {
                    "name": "end_day",
                    "field_type": "integer",
                    "min_value": 1,
                    "max_value": 31,
                    "default_value": 31,
                    "value": form.get_node_dict_value("end_day"),
                    "help_text": "The day of the month when the storage stops being "
                    + "calculated. Default to 31",
                },
                {
                    "name": "end_month",
                    "field_type": "integer",
                    "min_value": 1,
                    "max_value": 12,
                    "default_value": 12,
                    "value": form.get_node_dict_value("end_month"),
                    "help_text": "The month when the storage stops being calculated. "
                    + "Default to 12",
                },
                {
                    "name": "reset_to_initial_volume",
                    "field_type": "boolean",
                    "default_value": False,
                    "value": form.get_node_dict_value("reset_to_initial_volume"),
                    "help_text": "Reset the storage to its initial volume instead "
                    + "of its maximum volume each year",
                },
            ],
        )
