from pywr_editor.form import FieldConfig, FormSection, NodePickerWidget

from ..parameter_dialog_form import ParameterDialogForm


class DeficitParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialise the form section for a DeficitParameter.
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
                        help_text="The parameter provides the flow deficit for the "
                        "specified node above",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )
