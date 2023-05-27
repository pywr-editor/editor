from pywr_editor.form import FieldConfig, FloatWidget, FormSection

from ..parameter_dialog_form import ParameterDialogForm


class BinaryStepParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a BinaryStepParameter.
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
                        value=self.form.field_value("value"),
                        allow_empty=False,
                        help_text="This parameter returns the output below when the "
                        "reference value provided above is positive, zero otherwise. "
                        "This parameter is meant to be used in optimisation problems. "
                        "Default to 0",
                    ),
                    FieldConfig(
                        name="output",
                        field_type=FloatWidget,
                        default_value=1,
                        value=self.form.field_value("output"),
                        allow_empty=False,
                        help_text="The output returned by the parameter when Reference "
                        "value is positive. Default to 1",
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
