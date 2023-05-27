from pywr_editor.form import FieldConfig, FormSection, ParameterLineEditWidget

from ..parameter_dialog_form import ParameterDialogForm


class NegativeParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a NegativeParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="parameter",
                        field_type=ParameterLineEditWidget,
                        value=self.form.field_value("parameter"),
                        help_text="Reverse the sign of the provided parameter",
                    ),
                ]
            }
        )
