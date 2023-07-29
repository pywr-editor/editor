from pywr_editor.form import (
    ControlCurvesWidget,
    FieldConfig,
    FloatWidget,
    FormSection,
    StoragePickerWidget,
    Validation,
    ValuesAndExternalDataWidget,
)

from ..parameter_dialog_form import ParameterDialogForm


class ControlCurvePiecewiseInterpolatedParameterSection(FormSection):
    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict,
    ):
        """
        Initialises the form section for ControlCurvePiecewiseInterpolatedParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="storage_node",
                        field_type=StoragePickerWidget,
                        value=self.form.field_value("storage_node"),
                        help_text="Use the storage from the node specified above to "
                        "derive the parameter value",
                    ),
                    # this is always mandatory
                    FieldConfig(
                        # widget always returns a list of parameters
                        name="control_curves",
                        field_type=ControlCurvesWidget,
                        value={
                            "control_curve": self.form.field_value("control_curve"),
                            "control_curves": self.form.field_value("control_curves"),
                        },
                        help_text="Sort the control curves by the highest to the "
                        "lowest. The parameter linearly interpolates between the pair "
                        "of values specified below corresponding to the first control "
                        "curve that is above the node storage",
                    ),
                    FieldConfig(
                        name="values",
                        field_type=ValuesAndExternalDataWidget,
                        field_args={
                            "multiple_variables": True,
                            "show_row_numbers": True,
                            "row_number_label": "Above curve #",
                            "lower_bound": -pow(10, 6),
                            # values are provided by row
                            "transpose_values": True,
                            "variable_names": ["Largest value", "Smallest value"],
                        },
                        validate_fun=self._check_size,
                        value=self.form.field_value("values"),
                        help_text="The first value pair is used between the maximum and"
                        "the first control curve, the second pair between the first and"
                        " second curve, and so on until the last pair is reached to "
                        "interpolate between the last control curve and the minimum "
                        "storage",
                    ),
                    FieldConfig(
                        name="minimum",
                        label="Minimum storage",
                        field_type=FloatWidget,
                        field_args={"min_value": 0, "max_value": 1},
                        default_value=0,
                        value=self.form.field_value("minimum"),
                        help_text="The minimum storage between 0 and 1 to use for the "
                        "interpolation. Default to 0",
                    ),
                    FieldConfig(
                        name="maximum",
                        label="Maximum storage",
                        field_type=FloatWidget,
                        field_args={"min_value": 0, "max_value": 1},
                        default_value=1,
                        value=self.form.field_value("maximum"),
                        help_text="The maximum storage between 0 and 1 to use for the "
                        "interpolation. Default to 1",
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
        Checks that the number of values equals the number of control
        curves plus one.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        # noinspection PyTypeChecker
        control_curves_widget: ControlCurvesWidget = self.form.find_field(
            "control_curves"
        ).widget
        curves_size = len(control_curves_widget.get_value())
        expected_size = curves_size + 1

        # check size of nested data
        if curves_size and len(value[0]) != expected_size:
            return Validation(
                f"The number of values must be {expected_size} "
                f"(i.e. the number of control curves plus one)"
            )

        return Validation()

    def filter(self, form_data: dict) -> None:
        """
        Removes fields depending on the value set in source.
        :param form_data: The form data dictionary.
        :return: None.
        """
        # set "control_curve" or "control_curves" key
        curves = form_data["control_curves"]
        if len(curves) == 1:
            form_data["control_curve"] = curves[0]
            del form_data["control_curves"]
