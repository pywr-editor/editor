from typing import Type
from ..parameter_dialog_form import ParameterDialogForm
from pywr_editor.form import (
    ThresholdRelationSymbolWidget,
    ThresholdValuesWidget,
    ParameterLineEditWidget,
    FormSection,
    FormCustomWidget,
)
from pywr_editor.utils import Logging

"""
  Abstract section class to use for threshold
  parameters.
"""


class ValueDict:
    def __init__(
        self,
        widget: Type[FormCustomWidget],
        key: str,
        help_text: str | None = None,
    ):
        """
        Initialises the class.
        :param widget: The widget that provides the value to compare against the
        threshold. For example
        StoragePickerWidget for the StorageThresholdParameter.
        :param key: The dictionary key for the widget. For example "storage_node"
        for StorageThresholdParameter.
        :param help_text: The help text to use for the widget.
        """
        self.widget = widget
        self.key = key
        self.help_text = help_text


class AbstractThresholdParameterSection(FormSection):
    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict,
        log_name: str,
        threshold_description: str,
        value_dict: ValueDict | None = None,
    ):
        """
        Initialises the form section for a threshold parameters.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param value_dict: An instance of ValueDict that describes the field for
        the widget that provides the threshold value. Optional.
        :param threshold_description: The description to use for the "threshold" field.
        :param log_name: The name to use in the logger.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(log_name)

        if value_dict is not None:
            self.has_value_field = True
            self.value_widget = value_dict.widget
            self.value_key = value_dict.key
            self.value_help_text = value_dict.help_text
        else:
            self.has_value_field = False

        self.threshold_description = threshold_description

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
                    "name": "threshold",
                    "field_type": ParameterLineEditWidget,
                    "value": self.form.get_param_dict_value("threshold"),
                    "help_text": self.threshold_description
                    + ". The threshold can be a constant or a varying parameter "
                    + "(such as a profile or a time series)",
                },
                {
                    "name": "predicate",
                    "label": "Relation symbol",
                    "field_type": ThresholdRelationSymbolWidget,
                    "value": self.form.get_param_dict_value("predicate"),
                    "help_text": "This defines the predicate, which is the parameter's"
                    + " value above, followed by the relation symbol, followed by the "
                    + "threshold. For example, if the symbol is '>', Pywr  will assess "
                    + "the following predicate: parameter's value > threshold",
                },
                {
                    "name": "values",
                    "field_type": ThresholdValuesWidget,
                    "value": self.form.get_param_dict_value("values"),
                    "help_text": "If the predicate is false, this parameter will "
                    + "return  the left value above, otherwise the right value "
                    + "will be used. For example, if the predicate is '<' and the "
                    + " parameter's value is less than the threshold, the predicate "
                    + "is true and the right value is returned",
                },
                {
                    "name": "ratchet",
                    "field_type": "boolean",
                    "default_value": False,
                    "value": self.form.get_param_dict_value("ratchet"),
                    "help_text": "When Yes and once the predicate is true, the "
                    + "parameter value will not change anymore",
                },
            ],
            "Miscellaneous": [
                {
                    "name": "comment",
                    "value": self.form.get_param_dict_value("comment"),
                },
            ],
        }

        # for some parameters, it is not needed to specify a value to compare
        # (for example for CurrentOrdinalDayThresholdParameter)
        if self.has_value_field:
            # noinspection PyTypeChecker
            data_dict["Configuration"].insert(
                1,
                {
                    "name": self.value_key,
                    "field_type": self.value_widget,
                    "value": self.form.get_param_dict_value(self.value_key),
                    "help_text": self.value_help_text,
                },
            )

        return data_dict
