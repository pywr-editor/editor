from pywr_editor.form import (
    FieldConfig,
    FloatWidget,
    FormSection,
    ParameterLineEditWidget,
)

from ..parameter_dialog_form import ParameterDialogForm


class ScaledProfileParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a ScaledProfileParameter.
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
                        help_text="The parameter value to scale",
                    ),
                    FieldConfig(
                        name="scale",
                        field_type=FloatWidget,
                        default_value=None,
                        allow_empty=False,
                        value=self.form.field_value("scale"),
                        help_text="Scale the parameter value by the provided amount",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )
