from pywr_editor.form import FieldConfig, ParameterLineEditWidget

from ..node_dialog_form import NodeDialogForm
from .abstract_storage_section import AbstractStorageSection

"""
 Section for a Storage node. NOTE: the num_inputs
 and num_outputs property are mentioned in the manual,
 but are not used anywhere in the code. Therefore,
 they are not included in this section.
"""


class StorageSection(AbstractStorageSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a Storage.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.add_fields(
            {
                "Configuration": [
                    form.cost_field("storage"),
                    FieldConfig(
                        name="min_volume",
                        label="Minimum storage",
                        value=form.field_value("min_volume"),
                        field_type=ParameterLineEditWidget,
                        field_args={"is_mandatory": False},
                        default_value=0,
                        help_text="The minimum volume of the storage. Default to 0",
                    ),
                    FieldConfig(
                        name="max_volume",
                        label="Maximum storage",
                        value=form.field_value("max_volume"),
                        field_type=ParameterLineEditWidget,
                        field_args={"is_mandatory": False},
                        help_text="The maximum volume of the storage. Default to 0",
                    ),
                    form.initial_volume_field,
                    form.initial_volume_pc_field,
                ],
                "Level data": [
                    FieldConfig(
                        name="level",
                        value=form.field_value("level"),
                        field_type=ParameterLineEditWidget,
                        field_args={"is_mandatory": False},
                        help_text="A parameter providing the storage level. Optional",
                    ),
                    FieldConfig(
                        name="area",
                        value=form.field_value("area"),
                        field_type=ParameterLineEditWidget,
                        field_args={"is_mandatory": False},
                        help_text="A parameter providing the storage surface area. "
                        "Optional",
                    ),
                ],
                "Miscellaneous": [
                    form.comment,
                ],
            }
        )
