from pywr_editor.form import (
    FormSection,
    FormValidation,
    ParametersListPickerWidget,
    ScenarioPickerWidget,
)
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class ScenarioWrapperParameterSection(FormSection):
    def __init__(
        self,
        form,
        section_data,
    ):
        """
        Initialises the form section for a ScenarioWrapperParameter.
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

        data_dict = {
            "Configuration": [
                {
                    "name": "scenario",
                    "field_type": ScenarioPickerWidget,
                    "value": self.form.get_param_dict_value("scenario"),
                },
                {
                    "name": "parameters",
                    "label": "Parameters",
                    "field_type": ParametersListPickerWidget,
                    "validate_fun": self._check_size,
                    "value": self.form.get_param_dict_value("parameters"),
                    "help_text": "The parameter to use for each scenario ensemble. "
                    "You can provide parameters not explicitly supporting scenarios "
                    "(for example for control curves or interpolation parameters)",
                },
            ],
            "Miscellaneous": [self.form.comment],
        }

        return data_dict

    def _check_size(
        self,
        name: str,
        label: str,
        value: list[str | dict | float | int],
    ) -> FormValidation:
        """
        Checks that the number of parameters equals the scenario size.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        self.form: ParameterDialogForm

        scenario_field = self.form.find_field_by_name("scenario")
        size = self.form.model_config.scenarios.get_size_from_name(
            scenario_field.value()
        )

        if size is not None and len(value) != size:
            return FormValidation(
                validation=False,
                error_message=f"The number of parameters ({len(value)}) must match the "
                f"the scenario size ({size})",
            )

        return FormValidation(validation=True)
