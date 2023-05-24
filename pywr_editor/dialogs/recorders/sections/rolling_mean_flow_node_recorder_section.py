from pywr_editor.form import FieldConfig, NodePickerWidget, Validation

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class RollingMeanFlowNodeRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a RollingMeanFlowNodeRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=[
                FieldConfig(
                    name="node",
                    field_type=NodePickerWidget,
                    value=form.field_value("node"),
                    help_text="Store the mean flow through the node for the number of "
                    "time-steps or days provided below",
                ),
                FieldConfig(
                    name="timesteps",
                    label="Time-steps",
                    field_type="integer",
                    min_value=0,
                    default_value=0,
                    max_value=form.model_config.number_of_steps,
                    value=form.field_value("timesteps"),
                    help_text="The number of time-steps to calculate the mean flow "
                    "for. You can specify the number of days in the field below in "
                    "place of this",
                ),
                FieldConfig(
                    name="days",
                    field_type="integer",
                    value=form.field_value("days"),
                    min_value=0,
                    default_value=0,
                    max_value=form.model_config.number_of_steps
                    * form.model_config.time_delta,
                    help_text="The number of days to calculate the mean flow for",
                ),
            ],
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
