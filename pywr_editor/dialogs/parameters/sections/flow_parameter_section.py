from pywr_editor.form import FieldConfig, FloatWidget, FormSection, NodePickerWidget

from ..parameter_dialog_form import ParameterDialogForm


class FlowParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a FlowParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="node",
                        field_type=NodePickerWidget,
                        value=self.form.field_value("node"),
                        allow_empty=False,
                        help_text="The parameter provides the flow at the previous time"
                        "-step for the specified node",
                    ),
                    FieldConfig(
                        name="initial_value",
                        field_type=FloatWidget,
                        default_value=0,
                        field_args={"min_value": 0},
                        value=self.form.field_value("initial_value"),
                        allow_empty=False,
                        help_text="The value to return on the first time step when the "
                        "node does not have any past flow. Default to 0",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )
