from pywr_editor.form import (
    FieldConfig,
    FormSection,
    ParameterAggFuncWidget,
    ParametersListPickerWidget,
)

from ..parameter_dialog_form import ParameterDialogForm


class AggregatedParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a AggregatedParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="parameters",
                        field_type=ParametersListPickerWidget,
                        value=self.form.field_value("parameters"),
                        help_text="Aggregate the parameters using the aggregation "
                        "function specified below",
                    ),
                    FieldConfig(
                        name="agg_func",
                        label="Aggregation function",
                        field_type=ParameterAggFuncWidget,
                        value=self.form.field_value("agg_func"),
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )
