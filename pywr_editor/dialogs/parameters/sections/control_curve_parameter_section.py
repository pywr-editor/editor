from pywr_editor.form import (
    ControlCurveOptBoundsWidget,
    ControlCurveVariableIndicesWidget,
    FieldConfig,
)

from ..parameter_dialog_form import ParameterDialogForm
from .abstract_control_curve_parameter_section import (
    AbstractControlCurveParameterSection,
)


class ControlCurveParameterSection(AbstractControlCurveParameterSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a ControlCurveParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            values_size_increment=1,
            log_name=self.__class__.__name__,
        )

        self.form: ParameterDialogForm
        # add optimisation group
        self.fields_ = {
            "Configuration": self.fields_["Configuration"],
            self.form.optimisation_config_group_name: [
                self.form.is_variable_field,
                FieldConfig(
                    name="variable_indices",
                    field_type=ControlCurveVariableIndicesWidget,
                    value=self.form.field_value("variable_indices"),
                    help_text="If you want to make a subset of the 'Constant "
                    "values' variable, you can provide a list of zero-based indices "
                    "corresponding to the values which are to be considered "
                    "variables. This field is optional",
                ),
                FieldConfig(
                    name="lower_bounds",
                    field_type=ControlCurveOptBoundsWidget,
                    value=self.form.field_value("lower_bounds"),
                    help_text="The smallest values for the parameter during "
                    "optimisation",
                ),
                FieldConfig(
                    name="upper_bounds",
                    field_type=ControlCurveOptBoundsWidget,
                    value=self.form.field_value("upper_bounds"),
                    help_text="The largest values for the parameter during "
                    "optimisation",
                ),
            ],
            "Miscellaneous": self.fields_["Miscellaneous"],
        }

        # disable optimisation section
        if self.section_data["enable_optimisation_section"] is False:
            del self.fields_[self.form.optimisation_config_group_name]
