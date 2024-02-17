from typing import Any

from pywr_editor.form import (
    FieldConfig,
    FormSection,
    Validation,
    ValuesAndExternalDataWidget,
)

from ..parameter_dialog_form import ParameterDialogForm


class ArrayIndexedParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a ArrayIndexParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)

        self.form: ParameterDialogForm
        total_model_steps = self.form.model_config.number_of_steps
        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="values",
                        label="Known values",
                        field_type=ValuesAndExternalDataWidget,
                        field_args={
                            "show_row_numbers": True,
                            "row_number_label": "Timestep number",
                            "min_total_values": (
                                total_model_steps
                                if total_model_steps is not None
                                else None
                            ),
                        },
                        validate_fun=self._check_count,
                        value=self.form.field_value("values"),
                        help_text="Specify the values the parameter returns at each "
                        "step of the simulation",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )

    def _check_count(
        self,
        name: str,
        label: str,
        value: list[int | float] | dict[str, Any] | None,
    ) -> Validation:
        """
        Checks that the number of items in the list of numbers is the same as the
        number of time steps in the simulation. This only applies when the data
        source is from the table. Data from external files are not checked.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        self.form: ParameterDialogForm
        if isinstance(value, list):
            required_items = self.form.model_config.number_of_steps
            # do not force exact match
            if required_items is not None and len(value) < required_items:
                return Validation(
                    "You must provide at least the same number of values "
                    f"as the model time steps ({required_items})",
                )

        return Validation()
