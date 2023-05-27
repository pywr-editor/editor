from pywr_editor.form import FieldConfig, FloatWidget, FormSection

from ..node_dialog_form import NodeDialogForm


class AbstractNodeSection(FormSection):
    def __init__(
        self,
        form: NodeDialogForm,
        section_data: dict,
        add_conversion_factor: bool = True,
        additional_fields: list[dict] = None,
    ):
        """
        Initialises a general form section for a node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param add_conversion_factor: Whether to add the conversion factor field.
        Some nodes (like the BreakLink) do not make use of the parameter). Default
        to True.
        :param additional_fields: Additional fields to add to the section. Default to
        None.
        """
        super().__init__(form, section_data)
        self.add_conversion_factor = add_conversion_factor

        if not additional_fields:
            additional_fields = []

        # add conversion factor field before any additional fields
        if add_conversion_factor:
            additional_fields.append(
                FieldConfig(
                    name="conversion_factor",
                    field_type=FloatWidget,
                    field_args={"min_value": 0},
                    default_value=1,
                    value=form.field_value("conversion_factor"),
                    help_text="The conversion between inflow and outflow for the "
                    + "node",
                ),
            )
        self.add_fields(
            {
                "Configuration": [
                    form.min_flow_field,
                    form.max_flow_field,
                    form.cost_field("flow"),
                ]
                + additional_fields
                + [form.comment],
            }
        )
