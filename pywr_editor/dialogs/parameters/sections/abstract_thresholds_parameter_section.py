from pywr_editor.form import FormSection, ParametersListPickerWidget
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm
from .abstract_threshold_parameter_section import ValueDict

"""
  Abstract section class to use for threshold
  parameters supporting multiple thresholds and
  returning indexes.
"""


class AbstractThresholdsParameterSection(FormSection):
    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict,
        value_dict: ValueDict,
        log_name: str,
    ):
        """
        Initialises the form section for a DataFrameParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param value_dict: An instance of ValueDict that describes the field for the
        widget that provides the threshold value.
        :param log_name: The name to use in the logger.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(log_name)
        self.value_widget = value_dict.widget
        self.value_key = value_dict.key
        self.value_help_text = value_dict.help_text

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.logger.debug("Registering form")
        self.form: ParameterDialogForm

        data_dict = {
            "Configuration": [
                {
                    "name": self.value_key,
                    "field_type": self.value_widget,
                    "value": self.form.get_param_dict_value(self.value_key),
                    "help_text": self.value_help_text,
                },
                {
                    "name": "thresholds",
                    "field_type": ParametersListPickerWidget,
                    "value": self.form.get_param_dict_value("thresholds"),
                    "help_text": "The parameter returns an index based on the previous"
                    + "-day flow in the node specified above. For example, if one "
                    + "threshold is provided, then the index can be 0 (flow above the "
                    "threshold) or 1 (flow below). For two thresholds the index can "
                    + "be either 0 (above both), 1 (in between), or 2 (below both)",
                },
            ],
            "Miscellaneous": [
                {
                    "name": "comment",
                    "value": self.form.get_param_dict_value("comment"),
                },
            ],
        }

        return data_dict
