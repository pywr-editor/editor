from typing import Any

from pywr_editor.form import (
    FieldConfig,
    FloatWidget,
    FormSection,
    NodePickerWidget,
    Validation,
)

from ..parameter_dialog_form import ParameterDialogForm


class FlowDelayParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a FlowDelayParameter.
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
                        help_text="The parameter provides the flow at the previous "
                        "time-step for the specified node",
                    ),
                    FieldConfig(
                        name="timesteps",
                        field_type="integer",
                        default_value=0,
                        value=self.form.field_value("timesteps"),
                        validate_fun=self.check_timesteps,
                        min_value=0,
                        max_value=self.form.model_config.number_of_steps,
                        help_text="Number of time steps to delay the flow. Default to "
                        "0",
                    ),
                    FieldConfig(
                        name="days",
                        field_type="integer",
                        default_value=0,
                        value=self.form.field_value("days"),
                        validate_fun=self.check_days,
                        min_value=0,
                        help_text="Instead of provide the number of time step, delay "
                        "the flow by specifying the number of days. This number must "
                        "be exactly divisible by the time-step",
                    ),
                    FieldConfig(
                        name="initial_value",
                        field_type=FloatWidget,
                        field_args={"min_value": 0},
                        default_value=0,
                        value=self.form.field_value("initial_value"),
                        allow_empty=False,
                        help_text="The value to return on the first time step when the "
                        "node does not have any past flow. Default to 0",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )

    def check_days(self, name: str, label: str, value: int) -> Validation:
        """
        Checks that the number of days is divisible by the time step delta.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        self.form: ParameterDialogForm

        if value and value % self.form.model_config.time_delta != 0:
            return Validation(
                "The number must be exactly divisible by the "
                f"time step delta of {self.form.model_config.time_delta} day(s)",
            )

        return Validation()

    def check_timesteps(self, name: str, label: str, value: int) -> Validation:
        """
        Checks that the number of timesteps is larger than one when the "days" field
        is not provided.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        days = self.form.find_field("days").value()
        # check == 1 not <= 1, to return the message in validate() method
        if days == 0 and value == 1:
            return Validation("The number of time-steps must be must be larger than 1")

        return Validation()

    def validate(self, form_data: dict[str, Any]) -> Validation:
        """
        Validates the days and timesteps fields. Both fields cannot be provided at the
        same time
        :param form_data: The form data dictionary when the form validation is
        successful.
        :return: The Validation instance.
        """
        days_field = self.form.find_field("days")
        timesteps_field = self.form.find_field("timesteps")

        # both fields are set
        if days_field.value() and timesteps_field.value():
            return Validation(
                "You can provide the number of time steps or days, "
                "but not both values at the same time",
            )
        # none fields are set
        elif not days_field.value() and not timesteps_field.value():
            return Validation(
                "You must provide the number of time steps or days to set the delay"
            )
        return Validation()
