from pywr_editor.form import (
    FieldConfig,
    FloatWidget,
    FormSection,
    IntegerWidget,
    NodePickerWidget,
    Validation,
)

from ..parameter_dialog_form import ParameterDialogForm


class RollingMeanFlowNodeParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a RollingMeanFlowNodeParameter.
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
                        help_text="Store the mean flow through the node for the number "
                        "of time-steps or days provided below",
                    ),
                    FieldConfig(
                        name="timesteps",
                        label="Time-steps",
                        field_type=IntegerWidget,
                        field_args={"min_value": 0},
                        default_value=0,
                        max_value=self.form.model_config.number_of_steps,
                        value=self.form.field_value("timesteps"),
                        help_text="The number of time-steps to calculate the mean flow "
                        "for. You can specify the number of days in the field below in "
                        "place of this",
                    ),
                    FieldConfig(
                        name="days",
                        field_type=IntegerWidget,
                        field_args={
                            "min_value": 0,
                            "max_value": self.form.model_config.number_of_steps
                            * self.form.model_config.time_delta,
                        },
                        value=self.form.field_value("days"),
                        min_value=0,
                        default_value=0,
                        help_text="The number of days to calculate the mean flow for",
                    ),
                    FieldConfig(
                        name="initial_flow",
                        field_type=FloatWidget,
                        field_args={"min_value": 0},
                        value=self.form.field_value("initial_flow"),
                        default_value=0,
                        help_text="The initial value to use at the first model "
                        "time-step before any flows have been recorded. Default to 0",
                    ),
                ]
            }
        )

    def validate(self, form_data: dict) -> Validation:
        """
        Validates the days and timesteps fields. Both fields cannot be provided at the
        same time.
        :param form_data: The form data dictionary when the form validation is
        successful.
        :return: The Validation instance.
        """
        days_field = self.form.find_field("days")
        timesteps_field = self.form.find_field("timesteps")

        # both fields are set
        if days_field.value() > 0 and timesteps_field.value() > 0:
            return Validation(
                "You can provide the number of time steps or days, "
                "but not both values at the same time",
            )
        # none fields are set
        elif not days_field.value() and not timesteps_field.value():
            return Validation(
                "You must provide the number of time steps or days "
                "to calculate the rolling mean",
            )
        return Validation()
