from pywr_editor.form import (
    FormSection,
    IndexParametersListPickerWidget,
    ParameterAggFuncWidget,
)
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class AggregatedIndexParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a AggregatedIndexParameter.
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
                    "name": "parameters",
                    "field_type": IndexParametersListPickerWidget,
                    "value": self.form.get_param_dict_value("parameters"),
                    "help_text": "Aggregate the index parameters with the aggregation "
                    + "function specified below",
                },
                {
                    "name": "agg_func",
                    "field_type": ParameterAggFuncWidget,
                    "value": self.form.get_param_dict_value("agg_func"),
                },
            ],
            "Miscellaneous": [self.form.comment],
        }

        return data_dict
