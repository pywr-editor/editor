from pywr_editor.form import FieldConfig

from ..node_dialog_form import NodeDialogForm
from .abstract_virtual_storage_section import AbstractVirtualStorageSection


class MonthlyVirtualStorageSection(AbstractVirtualStorageSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a MonthlyVirtualStorage.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            additional_fields=[
                FieldConfig(
                    name="months",
                    label="Renewal month",
                    field_type="integer",
                    min_value=1,
                    max_value=12,
                    default_value=1,
                    value=form.field_value("months"),
                    help_text="Month of the year when to reset the storage "
                    "to its maximum volume. Default to 1",
                ),
                FieldConfig(
                    name="initial_months",
                    field_type="integer",
                    default_value=0,
                    min_value=0,
                    max_value=13,
                    value=form.field_value("initial_months"),
                    help_text="The number of months into the year the "
                    "storage is at when the model run starts. Default to 0. "
                    "If this is set to 3 and the 'Renewal month' to 5, 2 more months "
                    "will be needed to reset the virtual storage",
                ),
                FieldConfig(
                    name="reset_to_initial_volume",
                    field_type="boolean",
                    default_value=False,
                    value=form.field_value("reset_to_initial_volume"),
                    help_text="Reset the storage to its initial volume instead "
                    "of its maximum volume each year",
                ),
            ],
        )
