from pywr_editor.form import AbstractFloatListWidget, FormValidation, FormField


class ControlCurveOptBoundsWidget(AbstractFloatListWidget):
    def __init__(
        self,
        name: str,
        value: list[int] | None,
        parent: FormField,
    ):
        """
        Initialises the widget to handle the lower and upper bounds of an optimisation
        problem for a control curve parameter.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent widget.
        """
        super().__init__(
            name=name,
            value=value,
            log_name=self.__class__.__name__,
            only_list=True,
            parent=parent,
        )

    def validate(
        self, name: str, label: str, value: list[float]
    ) -> FormValidation:
        """
        Checks that the value is valid.
        :param name: The field name.
        :param label: The field label.
        :param value: The field label. This is not used.
        :return: The FormValidation instance.
        """
        validation_output = super().validate(name, label, value)
        if validation_output.validation is False:
            return validation_output

        bounds = self.get_value()
        # bounds are provided
        if bounds:
            # this field is mandatory if variable_indices is set
            var_indices_field = self.form.find_field_by_name("variable_indices")
            if not var_indices_field.value():
                return FormValidation(
                    validation=False,
                    error_message="You can set this field only if you have set the "
                    + f"'{var_indices_field.label}' field",
                )

            # "values" key must be selected
            values_source_field = self.form.find_field_by_name("values_source")
            if values_source_field.value() != "values":
                return FormValidation(
                    validation=False,
                    error_message="You can set this field only if you have set the "
                    + "'Constant values' field as source",
                )

            # the number of bounds must be the same as variable_indices
            if len(bounds) != len(var_indices_field.value()):
                return FormValidation(
                    validation=False,
                    error_message="The number of bounds must be the same as the "
                    + f"number of indices provided in the '{var_indices_field.label}'"
                    + " field",
                )

        return validation_output
