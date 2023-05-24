from pywr_editor.form import (
    FieldConfig,
    FormSection,
    ParametersListPickerWidget,
    ScenarioPickerWidget,
    Validation,
)

from ..parameter_dialog_form import ParameterDialogForm


class ScenarioWrapperParameterSection(FormSection):
    def __init__(self, form, section_data):
        """
        Initialises the form section for a ScenarioWrapperParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="scenario",
                        field_type=ScenarioPickerWidget,
                        value=self.form.field_value("scenario"),
                    ),
                    FieldConfig(
                        name="parameters",
                        label="Parameters",
                        field_type=ParametersListPickerWidget,
                        validate_fun=self._check_size,
                        value=self.form.field_value("parameters"),
                        help_text="The parameter to use for each scenario ensemble. "
                        "You can provide parameters not explicitly supporting scenarios"
                        " (for example for control curves or interpolation parameters)",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )

    def _check_size(
        self,
        name: str,
        label: str,
        value: list[str | dict | float | int],
    ) -> Validation:
        """
        Checks that the number of parameters equals the scenario size.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        self.form: ParameterDialogForm

        scenario_field = self.form.find_field("scenario")
        size = self.form.model_config.scenarios.get_size(scenario_field.value())

        if size is not None and len(value) != size:
            return Validation(
                f"The number of parameters ({len(value)}) must match the "
                f"the scenario size ({size})",
            )

        return Validation()
