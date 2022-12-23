from pywr_editor.form import ParameterLineEditWidget, TableValuesWidget
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm
from .abstract_interpolation_section import AbstractInterpolationSection


class InterpolatedQuadratureParameterSection(AbstractInterpolationSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a InterpolatedQuadratureParameter.
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
                    # this field includes both x and y values
                    "name": "x_y_values",
                    "label": "Known data points",
                    "field_type": TableValuesWidget,
                    "field_args": {"min_total_values": 2},
                    "value": {
                        "x": self.form.get_param_dict_value("x"),
                        "y": self.form.get_param_dict_value("y"),
                    },
                    "help_text": "Use the data points above to define the "
                    + "interpolation function. This is then integrated using "
                    + "the Gaussian quadrature between the bounds provided by "
                    + "the parameters below",
                },
                {
                    "name": "upper_parameter",
                    "field_type": ParameterLineEditWidget,
                    "value": self.form.get_param_dict_value("upper_parameter"),
                    "help_text": "Upper value of the interpolated interval to "
                    + "integrate over",
                },
                {
                    "name": "lower_parameter",
                    "field_type": ParameterLineEditWidget,
                    "field_args": {"is_mandatory": False},
                    "value": self.form.get_param_dict_value("lower_parameter"),
                    "help_text": "Upper value of the interpolated interval to "
                    + "integrate over. If omitted this will be assumed to be zero",
                },
            ],
            "Interpolation settings": self.interp_settings,
            "Miscellaneous": [
                {
                    "name": "comment",
                    "value": self.form.get_param_dict_value("comment"),
                },
            ],
        }

        return data_dict

    # noinspection PyMethodMayBeStatic
    def filter(self, form_data: dict) -> None:
        """
        Removes fields depending on the value set in source.
        :param form_data: The form data dictionary.
        :return: None.
        """
        # split x and y
        for var_name, var_values in form_data["x_y_values"].items():
            form_data[var_name] = var_values
        del form_data["x_y_values"]
