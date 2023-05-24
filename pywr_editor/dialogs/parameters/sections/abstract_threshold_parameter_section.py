from typing import Type

from pywr_editor.form import (
    BooleanWidget,
    FieldConfig,
    FormCustomWidget,
    FormSection,
    ParameterLineEditWidget,
    ThresholdRelationSymbolWidget,
    ThresholdValuesWidget,
)

from ..parameter_dialog_form import ParameterDialogForm

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
        value_rel_symbol_description: str,
        value_dict: ValueDict | None = None,
    ):
        """
        Initialises the form section for a threshold parameters.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param value_dict: An instance of ValueDict that describes the field for
        the widget that provides the threshold value. Optional.
        :param threshold_description: The description to use for the "threshold" field.
        :param value_rel_symbol_description: The description to insert in the help text
        of the relation symbol to define the value to compare in the predicate.
        :param log_name: The name to use in the logger.
        """
        super().__init__(form, section_data)

        if value_dict is not None:
            self.has_value_field = True
            self.value_widget = value_dict.widget
            self.value_key = value_dict.key
            self.value_help_text = value_dict.help_text
        else:
            self.has_value_field = False

        self.threshold_description = threshold_description
        self.value_rel_symbol_description = value_rel_symbol_description

        self.form: ParameterDialogForm
        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="threshold",
                        field_type=ParameterLineEditWidget,
                        value=self.form.field_value("threshold"),
                        help_text=self.threshold_description
                        + ". The threshold can be a constant or a varying parameter "
                        "(such as a profile or a time series)",
                    ),
                    FieldConfig(
                        name="predicate",
                        label="Relation symbol",
                        field_type=ThresholdRelationSymbolWidget,
                        value=self.form.field_value("predicate"),
                        help_text="This defines the predicate, which is the "
                        f"{self.value_rel_symbol_description}, followed by the "
                        "relation symbol, followed by the threshold. For example, if "
                        "the symbol is '>', Pywr  will assess the following predicate: "
                        f"{self.value_rel_symbol_description} > threshold",
                    ),
                    FieldConfig(
                        name="values",
                        field_type=ThresholdValuesWidget,
                        value=self.form.field_value("values"),
                        help_text="If the predicate is false, this parameter will "
                        "return  the left value above, otherwise the right value "
                        "will be used. For example, if the predicate is '<' and the "
                        f"{self.value_rel_symbol_description} is less than the "
                        "threshold, the predicate is true and the right value is "
                        "returned",
                    ),
                    FieldConfig(
                        name="ratchet",
                        field_type=BooleanWidget,
                        default_value=False,
                        value=self.form.field_value("ratchet"),
                        help_text="When Yes and once the predicate is true, the "
                        "parameter value will not change anymore",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )

        # for some parameters, it is not needed to specify a value to compare
        # (for example for CurrentOrdinalDayThresholdParameter)
        if self.has_value_field:
            self.fields_["Configuration"].insert(
                1,
                FieldConfig(
                    name=self.value_key,
                    field_type=self.value_widget,
                    value=self.form.field_value(self.value_key),
                    help_text=self.value_help_text,
                ),
            )
