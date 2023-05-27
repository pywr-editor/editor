from pywr_editor.form import (
    FieldConfig,
    NodesAndFactorsTableWidget,
    ParameterLineEditWidget,
)

from ..node_dialog_form import NodeDialogForm
from .abstract_storage_section import AbstractStorageSection

"""
 Defines a section for a virtual storage. Note that
 the cost field is omitted because the node raise
 an error if the cost is not zero.
"""


class AbstractVirtualStorageSection(AbstractStorageSection):
    def __init__(
        self,
        form: NodeDialogForm,
        section_data: dict,
        additional_fields: list[dict] = None,
    ):
        """
        Initialises an abstract form section for a virtual storage.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param additional_fields: Additional fields to add to the section. Default to
        None.
        """
        super().__init__(form, section_data)
        if not additional_fields:
            additional_fields = []

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="nodes_and_factors",
                        field_type=NodesAndFactorsTableWidget,
                        value={
                            "nodes": form.field_value("nodes"),
                            "factors": form.field_value("factors"),
                        },
                        help_text="Provide a list of inflow/outflow nodes to use to "
                        "calculate the storage. Additional factors can also be provided"
                        " to scale the nodes' flows. Positive factors remove water from"
                        " the storage, negative factors preserve it",
                    ),
                    FieldConfig(
                        name="min_volume",
                        label="Minimum storage",
                        value=form.field_value("min_volume"),
                        field_type=ParameterLineEditWidget,
                        field_args={"is_mandatory": False},
                        default_value=0,
                        help_text="The minimum volume the storage is allowed to reach. "
                        "If zero, the nodes will generate no flow. When omitted it "
                        "defaults to 0",
                    ),
                    FieldConfig(
                        name="max_volume",
                        label="Maximum storage",
                        value=form.field_value("max_volume"),
                        field_type=ParameterLineEditWidget,
                        field_args={"is_mandatory": False},
                        help_text="The maximum volume the storage is allowed to reach. "
                        "Once this virtual node reaches its maximum, the flow through "
                        "the will stop. Leave it empty to ignore this constraint",
                    ),
                    form.initial_volume_field,
                    form.initial_volume_pc_field,
                ]
                + additional_fields
                + [
                    form.comment,
                ],
            }
        )
