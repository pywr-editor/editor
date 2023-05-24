from pywr_editor.form import FieldConfig, FormSection, ParameterLineEditWidget

from ..node_dialog_form import NodeDialogForm


class CatchmentSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises a form section for a Catchment node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="flow",
                        label="Maximum flow",
                        field_type=ParameterLineEditWidget,
                        field_args={"is_mandatory": False},
                        value=form.field_value("flow"),
                        help_text="The inflow from the catchment. Default to 0",
                    ),
                    form.cost_field("flow"),
                    form.comment,
                ],
            }
        )
