from pywr_editor.form import FieldConfig, FloatWidget, FormSection

from ..parameter_dialog_form import ParameterDialogForm


class RectifierParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a RectifierParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)

        self.form: ParameterDialogForm
        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="value",
                        label="Reference value",
                        field_type=FloatWidget,
                        default_value=0,
                        allow_empty=False,
                        value=self.form.field_value("value"),
                        help_text="This parameter returns an output between the Min "
                        "output and Max output values provided below based on the "
                        "following equation: Min output + (Max output - Min output) * "
                        "Reference value / Upper bound\nIn particular, zero is returned"
                        " when Reference value is negative, otherwise Max output is "
                        "returned when the function value is at its upper bound. "
                        "Default to 0",
                    ),
                    FieldConfig(
                        name="min_output",
                        label="Minimum output",
                        field_type=FloatWidget,
                        default_value=0,
                        value=self.form.field_value("min_output"),
                        allow_empty=False,
                        help_text="The minimum output returned by the parameter. "
                        "Default to 0",
                    ),
                    FieldConfig(
                        name="max_output",
                        label="Maximum output",
                        field_type=FloatWidget,
                        default_value=1,
                        value=self.form.field_value("max_output"),
                        allow_empty=False,
                        help_text="The maximum output returned by the parameter. "
                        "Default to 1",
                    ),
                ],
                self.form.optimisation_config_group_name: [
                    self.form.is_variable_field,
                    FieldConfig(
                        name="lower_bounds",
                        label="Lower bound",
                        field_type=FloatWidget,
                        default_value=-1,
                        value=self.form.field_value("lower_bounds"),
                        allow_empty=False,
                        help_text="The smallest value during optimisation. "
                        "Default to -1",
                    ),
                    FieldConfig(
                        name="upper_bounds",
                        label="Upper bound",
                        field_type=FloatWidget,
                        default_value=1,
                        value=self.form.field_value("upper_bounds"),
                        allow_empty=False,
                        help_text="The largest value during optimisation. "
                        "Default to 1",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )

        # disable optimisation section
        if self.section_data["enable_optimisation_section"] is False:
            del self.fields_[self.form.optimisation_config_group_name]
