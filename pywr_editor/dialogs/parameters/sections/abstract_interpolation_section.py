from pywr_editor.form import (
    FieldConfig,
    FormSection,
    InterpFillValueWidget,
    InterpKindWidget,
)

from ..parameter_dialog_form import ParameterDialogForm


class AbstractInterpolationSection(FormSection):
    @property
    def interp_settings(self) -> list[dict]:
        """
        Returns the list of widgets with the interpolation settings. See
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html#scipy.interpolate.interp1d
        :return: The list of dictionaries to set up the form.
        """
        self.form: ParameterDialogForm
        return [
            FieldConfig(
                name="kind",
                label="Interpolation type",
                field_type=InterpKindWidget,
                value=self.form.field_value("kind"),
                help_text="Specify the interpolation function",
            ),
            FieldConfig(
                name="fill_value",
                label="Fill value for extrapolation",
                field_type=InterpFillValueWidget,
                value=self.form.field_value("fill_value"),
                help_text="Choose 'Extrapolate' to extrapolate points outside the "
                "data range. Otherwise you can provide a comma-separated list of two "
                "values to use for y when x is outside its lower or upper bound. "
                "The first value is when x < lower bound, the second one when x > "
                "upper bound",
            ),
            FieldConfig(
                name="bounds_error",
                label="Fail on extrapolation",
                field_type="boolean",
                default_value=True,
                value=self.form.field_value("bounds_error"),
                help_text="Raise an error when the interpolation provides a value "
                "outside of the range of x",
            ),
            FieldConfig(
                name="assume_sorted",
                label="Disable sorting",
                field_type="boolean",
                default_value=False,
                value=self.form.field_value("assume_sorted"),
                help_text="When No, values of x are sorted first to ensure a "
                "proper interpolation. If performance is critical, sorting can be "
                "turned off, but values must already be monotonically increasing",
            ),
        ]
