from pywr_editor.form import FormValidation, NodePickerWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class RollingMeanFlowNodeRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a RollingMeanFlowNodeRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        self.time_delta = form.model_config.time_delta
        fields = [
            {
                "name": "node",
                "field_type": NodePickerWidget,
                "value": form.get_recorder_dict_value("node"),
                "help_text": "Store the mean flow through the node for the number of "
                + "time-steps or days provided below",
            },
            {
                "name": "timesteps",
                "label": "Time-steps",
                "field_type": "integer",
                "min_value": 0,
                "default_value": 0,
                "max_value": form.model_config.number_of_steps,
                "value": form.get_recorder_dict_value("timesteps"),
                "help_text": "The number of time-steps to calculate the mean flow "
                + "for. You can specify the number of days in the field below in "
                + "place of this",
            },
            {
                "name": "days",
                "field_type": "integer",
                "value": form.get_recorder_dict_value("days"),
                "min_value": 0,
                "default_value": 0,
                "max_value": form.model_config.number_of_steps
                * form.model_config.time_delta,
                "help_text": "The number of days to calculate the mean flow for",
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            log_name=self.__class__.__name__,
        )

    def validate(self, form_data: dict) -> FormValidation:
        """
        Validates the days and timesteps fields. Both fields cannot be provided at the
        same time.
        :param form_data: The form data dictionary when the form validation is
        successful.
        :return: The FormValidation instance.
        """
        days_field = self.form.find_field_by_name("days")
        timesteps_field = self.form.find_field_by_name("timesteps")

        # both fields are set
        if days_field.value() > 0 and timesteps_field.value() > 0:
            return FormValidation(
                validation=False,
                error_message="You can provide the number of time steps or days, "
                "but not both values at the same time",
            )
        # none fields are set
        elif not days_field.value() and not timesteps_field.value():
            return FormValidation(
                validation=False,
                error_message="You must provide the number of time steps or days "
                "to calculate the rolling mean",
            )
        return FormValidation(validation=True)
