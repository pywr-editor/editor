from pywr_editor.form import FieldConfig, NodePickerWidget, TableValuesWidget

from ..parameter_dialog_form import ParameterDialogForm
from .abstract_interpolation_section import AbstractInterpolationSection


class InterpolatedFlowParameterSection(AbstractInterpolationSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a InterpolatedFlowParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="node",
                        field_type=NodePickerWidget,
                        value=self.form.field_value("node"),
                        help_text="This parameter returns an interpolated value using "
                        "the input flow to the node provided above",
                    ),
                    FieldConfig(
                        # this field includes both x and y values
                        name="x_y_values",
                        label="Known data points",
                        field_type=TableValuesWidget,
                        field_args={"min_total_values": 2},
                        value={
                            "flows": self.form.field_value("flows"),
                            "y": self.form.field_value("y"),
                        },
                        help_text="Use the data points above for the interpolation",
                    ),
                ],
                "Interpolation settings": self.interp_settings,
                "Miscellaneous": [self.form.comment],
            }
        )

    # noinspection PyMethodMayBeStatic
    def filter(self, form_data: dict) -> None:
        """
        Splits the data points dictionary.
        :param form_data: The form data dictionary.
        :return: None.
        """
        # split x and y
        for var_name, var_values in form_data["x_y_values"].items():
            form_data[var_name] = var_values
        del form_data["x_y_values"]
