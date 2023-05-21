from typing import Any

from pywr_editor.form import FormSection, FormValidation
from pywr_editor.utils import Logging

from ..node_dialog_form import NodeDialogForm


class DelayNodeSection(FormSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a DelayNode.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form = form
        self.logger = Logging().logger(self.__class__.__name__)

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.logger.debug("Registering form")

        data_dict = {
            "Configuration": [
                # fields from FlowDelayParameterSection. Pywr passes these
                # options to the delay parameter
                {
                    "name": "timesteps",
                    "field_type": "integer",
                    "default_value": 0,
                    "value": self.form.get_node_dict_value("timesteps"),
                    "validate_fun": self.check_timesteps,
                    "min_value": 0,
                    "max_value": self.form.model_config.number_of_steps,
                    "help_text": "Number of time steps to delay the flow. Default to "
                    "0",
                },
                {
                    "name": "days",
                    "field_type": "integer",
                    "default_value": 0,
                    "value": self.form.get_node_dict_value("days"),
                    "validate_fun": self.check_days,
                    "min_value": 0,
                    "help_text": "Instead of provide the number of time step, delay "
                    "the flow by specifying the number of days. This number must be "
                    "exactly divisible by the time-step",
                },
                self.form.comment,
            ],
        }

        return data_dict

    def check_days(self, name: str, label: str, value: int) -> FormValidation:
        """
        Checks that the number of days is divisible by the time step delta.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        if value and value % self.form.model_config.time_delta != 0:
            return FormValidation(
                validation=False,
                error_message="The number must be exactly divisible by the "
                f"time step delta of {self.form.model_config.time_delta} day(s)",
            )

        return FormValidation(validation=True)

    def check_timesteps(self, name: str, label: str, value: int) -> FormValidation:
        """
        Checks that the number of timesteps is larger than one when the "days" field
        is not provided.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        days = self.form.find_field_by_name("days").value()
        # check == 1 not <= 1, to return the message in validate() method
        if days == 0 and value == 1:
            return FormValidation(
                validation=False,
                error_message="The number of time-steps must be must be larger than 1",
            )

        return FormValidation(validation=True)

    def validate(self, form_data: dict[str, Any]) -> FormValidation:
        """
        Validates the "days" and time"steps fields. Both fields cannot be provided
        at the same time.
        :param form_data: The form data dictionary when the form validation is
        successful.
        :return: The FormValidation instance.
        """
        days_field = self.form.find_field_by_name("days")
        timesteps_field = self.form.find_field_by_name("timesteps")

        # both fields are set
        if days_field.value() and timesteps_field.value():
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
                "to set the delay",
            )
        return FormValidation(validation=True)
