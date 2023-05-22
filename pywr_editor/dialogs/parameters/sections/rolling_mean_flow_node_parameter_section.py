from pywr_editor.form import FormSection, NodePickerWidget, Validation
from pywr_editor.form.widgets.float_widget import FloatWidget
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class RollingMeanFlowNodeParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a RollingMeanFlowNodeParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(self.__class__.__name__)

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.form: ParameterDialogForm
        self.logger.debug("Registering form")

        return {
            "Configuration": [
                {
                    "name": "node",
                    "field_type": NodePickerWidget,
                    "value": self.form.get_param_dict_value("node"),
                    "help_text": "Store the mean flow through the node for the number "
                    + "of time-steps or days provided below",
                },
                {
                    "name": "timesteps",
                    "label": "Time-steps",
                    "field_type": "integer",
                    "min_value": 0,
                    "default_value": 0,
                    "max_value": self.form.model_config.number_of_steps,
                    "value": self.form.get_param_dict_value("timesteps"),
                    "help_text": "The number of time-steps to calculate the mean flow "
                    + "for. You can specify the number of days in the field below in "
                    + "place of this",
                },
                {
                    "name": "days",
                    "field_type": "integer",
                    "value": self.form.get_param_dict_value("days"),
                    "min_value": 0,
                    "default_value": 0,
                    "max_value": self.form.model_config.number_of_steps
                    * self.form.model_config.time_delta,
                    "help_text": "The number of days to calculate the mean flow for",
                },
                {
                    "name": "initial_flow",
                    "field_type": FloatWidget,
                    "field_args": {"min_value": 0},
                    "value": self.form.get_param_dict_value("initial_flow"),
                    "default_value": 0,
                    "help_text": "The initial value to use at the first model timestep "
                    + "before any flows have been recorded. Default to 0",
                },
            ]
        }

    def validate(self, form_data: dict) -> Validation:
        """
        Validates the days and timesteps fields. Both fields cannot be provided at the
        same time.
        :param form_data: The form data dictionary when the form validation is
        successful.
        :return: The Validation instance.
        """
        days_field = self.form.find_field_by_name("days")
        timesteps_field = self.form.find_field_by_name("timesteps")

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
