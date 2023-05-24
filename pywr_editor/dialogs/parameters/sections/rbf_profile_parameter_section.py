from pywr_editor.form import (
    FieldConfig,
    FloatWidget,
    FormSection,
    RbfDayOfYearWidget,
    RbfFunction,
    RbfOptBoundWidget,
    RbfValues,
    Validation,
)

from ..parameter_dialog_form import ParameterDialogForm


class RbfProfileParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a RbfProfileParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="days_of_year",
                        label="Days of the year",
                        field_type=RbfDayOfYearWidget,
                        help_text="The days of the year at which the interpolation "
                        "nodes are defined. The first value must be one",
                        value=self.form.field_value("days_of_year"),
                        validate_fun=self._check_day_of_year,
                    ),
                    FieldConfig(
                        name="values",
                        field_type=RbfValues,
                        help_text="Nodes to use for interpolation corresponding to the "
                        "days of the year",
                        value=self.form.field_value("values"),
                        validate_fun=self._check_count,
                    ),
                    FieldConfig(
                        name="max_value",
                        field_type=FloatWidget,
                        help_text="Cap the interpolated daily profile to the provided "
                        "maximum value. Optional",
                        value=self.form.field_value("max_value"),
                    ),
                    FieldConfig(
                        name="min_value",
                        field_type=FloatWidget,
                        help_text="Cap the interpolated daily profile to the provided "
                        "minimum value. Optional",
                        value=self.form.field_value("min_value"),
                    ),
                ],
                # from https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.Rbf.html # noqa: E501
                "Interpolation settings": [
                    FieldConfig(
                        name="function",
                        label="Radial basis function",
                        field_type=RbfFunction,
                        help_text="Function to use for the interpolation. "
                        "Default is 'Multiquadric'",
                        value=self.form.field_value("function"),
                    ),
                    FieldConfig(
                        name="epsilon",
                        field_type=FloatWidget,
                        help_text="Adjustable constant for gaussian for multi-quadratic"
                        " functions only. Optional",
                        value=self.form.field_value("epsilon"),
                    ),
                    FieldConfig(
                        name="smooth",
                        field_type=FloatWidget,
                        default_value=0,
                        help_text="Change the smoothness of the approximation. "
                        "Optional",
                        value=self.form.field_value("smooth"),
                    ),
                ],
                "Miscellaneous": [self.form.comment],
                self.form.optimisation_config_group_name: [
                    self.form.is_variable_field,
                    FieldConfig(
                        name="lower_bounds",
                        field_type=RbfOptBoundWidget,
                        label="Value lower bounds",
                        value=self.form.field_value("lower_bounds"),
                        validate_fun=self._check_count,
                        help_text="The smallest value for the parameter during "
                        "optimisation. This can be a number, to use the same bound for "
                        "all values in the 'Values' field, or comma-separated values to"
                        " bound each value",
                    ),
                    FieldConfig(
                        name="upper_bounds",
                        field_type=RbfOptBoundWidget,
                        label="Value upper bounds",
                        value=self.form.field_value("upper_bounds"),
                        validate_fun=self._check_count,
                        help_text="The largest value for the parameter during "
                        "optimisation. This can be a number, to use the same bound for "
                        "all values in the 'Values' field, or comma-separated values to"
                        " bound each value",
                    ),
                    FieldConfig(
                        name="variable_days_of_year_range",
                        label="Days of the year bounds",
                        field_type="integer",
                        default_value=0,
                        # limits depend on set value; use 365
                        min_value=-365,
                        max_value=365,
                        suffix="days",
                        value=self.form.field_value("variable_days_of_year_range"),
                        validate_fun=self._check_day_range,
                        help_text="This allows the values in the 'Days of the year' "
                        "field to vary by the specified amount. The shift can be "
                        "positive or negative and affects all days except the first "
                        "day, which is always 1",
                    ),
                ],
            }
        )

        # disable optimisation section
        if self.section_data["enable_optimisation_section"] is False:
            del self.fields_[self.form.optimisation_config_group_name]

    def _check_count(self, name: str, label: str, value: list) -> Validation:
        """
        Checks that the number of items in "value" is the same as in the
        "days_of_year" field.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        days = self.form.find_field("days_of_year")
        days_value = days.value()
        days_label = self.form.get_label("days_of_year")

        if (
            isinstance(value, list)
            and isinstance(days_value, list)
            and len(days_value) != len(value)
        ):
            return Validation(
                "The number of items must be the same as in "
                f"the '{days_label}' fields",
            )

        return Validation()

    @staticmethod
    def _check_day_of_year(name: str, label: str, value: list) -> Validation:
        """
        Checks that "days_of_year" contains valid values.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        if isinstance(value, list):
            # this mirrors pywr check
            if value[0] != 1:
                return Validation("The first item must be 1")
            elif len(value) < 3:
                return Validation("You need to provide at least 3 items")
            elif any([j - i <= 0 for i, j in zip(value[:-1], value[1:])]):
                return Validation("The items must be strictly monotonically increasing")
            elif max(value) > 365 or min(value) < 0:
                return Validation("The items must be between 1 and 365 inclusive")
        return Validation()

    def _check_day_range(self, name: str, label: str, value: list) -> Validation:
        """
        Checks the range for the "days_of_year" during optimisation.
        :param name: The field name.
        :param label: The field label.
        :param value: THe field value.
        :return: The validation instance.
        """
        days = self.form.find_field("days_of_year")
        days_value = days.value()
        if not isinstance(days_value, list):
            return Validation()

        day_spacing_valid = any(
            [j - i <= 2 * value for i, j in zip(days_value[:-1], days_value[1:])]
        )
        if value != 0 and day_spacing_valid:
            days_label = self.form.get_label("days_of_year")

            return Validation(
                "To ensure a proper optimisation, the distance between "
                f"this value and any day in the '{days_label}' field should be less "
                "than half the minimum spacing between the days of the year. Reduce "
                "this value or increase the separation between the days of the year",
            )

        return Validation()
