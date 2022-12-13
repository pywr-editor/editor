from ..parameter_dialog_form import ParameterDialogForm
from .abstract_control_curve_parameter_section import (
    AbstractControlCurveParameterSection,
)
from pywr_editor.form import (
    ControlCurveOptBoundsWidget,
    ControlCurveVariableIndicesWidget,
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

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.form: ParameterDialogForm
        data_dict = super().data

        # add optimisation group
        data_dict = {
            "Configuration": data_dict["Configuration"],
            self.form.optimisation_config_group_name: [
                self.form.is_variable_field,
                {
                    "name": "variable_indices",
                    "field_type": ControlCurveVariableIndicesWidget,
                    "value": self.form.get_param_dict_value("variable_indices"),
                    "help_text": "If you want to make a subset of the 'Constant "
                    "values' variable, you can provide a list of zero-based indices "
                    "corresponding to the values which are to be considered "
                    "variables. This field is optional",
                },
                {
                    "name": "lower_bounds",
                    "field_type": ControlCurveOptBoundsWidget,
                    "value": self.form.get_param_dict_value("lower_bounds"),
                    "help_text": "The smallest values for the parameter during "
                    "optimisation",
                },
                {
                    "name": "upper_bounds",
                    "field_type": ControlCurveOptBoundsWidget,
                    "value": self.form.get_param_dict_value("upper_bounds"),
                    "help_text": "The largest values for the parameter during "
                    "optimisation",
                },
            ],
            "Miscellaneous": data_dict["Miscellaneous"],
        }

        # disable optimisation section
        if self.section_data["enable_optimisation_section"] is False:
            del data_dict[self.form.optimisation_config_group_name]

        return data_dict
