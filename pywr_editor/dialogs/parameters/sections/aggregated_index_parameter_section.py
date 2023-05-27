from pywr_editor.form import (
    FieldConfig,
    FormSection,
    IndexParametersListPickerWidget,
    ParameterAggFuncWidget,
)

from ..parameter_dialog_form import ParameterDialogForm


class AggregatedIndexParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a AggregatedIndexParameter.
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
                        field_type=IndexParametersListPickerWidget,
                        value=self.form.field_value("parameters"),
                        help_text="Aggregate the index parameters with the aggregation"
                        " function specified below",
                    ),
                    FieldConfig(
                        name="agg_func",
                        field_type=ParameterAggFuncWidget,
                        value=self.form.field_value("agg_func"),
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )
