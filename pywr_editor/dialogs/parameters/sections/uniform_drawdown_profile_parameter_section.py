from pywr_editor.form import FieldConfig, FormSection, IntegerWidget

from ..parameter_dialog_form import ParameterDialogForm


class UniformDrawdownProfileParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a UniformDrawdownProfileParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="reset_day",
                        field_type=IntegerWidget,
                        field_args={"min_value": 1, "max_value": 31},
                        help_text="The day of the month (1-31) to reset the volume to "
                        "the initial value",
                        value=self.form.field_value("reset_day"),
                    ),
                    FieldConfig(
                        name="reset_month",
                        field_type=IntegerWidget,
                        field_args={"min_value": 1, "max_value": 12},
                        help_text="The month (1-12) to reset the volume to the initial "
                        "value",
                        value=self.form.field_value("reset_month"),
                    ),
                    FieldConfig(
                        name="residual_days",
                        field_type=IntegerWidget,
                        field_args={"max_value": 366},
                        default_value=0,
                        help_text="The number of days of residual licence to target at "
                        "the end of the calendar year",
                        value=self.form.field_value("residual_days"),
                    ),
                ]
            }
        )
