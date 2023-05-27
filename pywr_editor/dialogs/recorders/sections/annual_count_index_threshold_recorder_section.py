from pywr_editor.form import (
    AbstractFloatListWidget,
    DayMonthWidget,
    FieldConfig,
    FloatWidget,
    ParametersListPickerWidget,
    Validation,
)

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_numpy_recorder_section import (
    AbstractNumpyRecorderSection,
    TemporalWidgetField,
)


class AnnualCountIndexThresholdRecorderSection(AbstractNumpyRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a AnnualCountIndexThresholdRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            FieldConfig(
                name="parameters",
                field_type=ParametersListPickerWidget,
                value=form.field_value("parameters"),
                help_text="For each scenario, store the number of years when at "
                "least one of the parameters exceeds the threshold provided below",
            ),
            FieldConfig(
                name="threshold",
                field_type=FloatWidget,
                value=form.field_value("threshold"),
                help_text="Threshold to compare the parameter values against",
            ),
        ]
        additional_sections = {
            "Filters": [
                FieldConfig(
                    name="exclude_months",
                    label="Exclude months",
                    field_type=AbstractFloatListWidget,
                    field_args={
                        "allowed_item_types": int,
                        "only_list": True,
                        "final_type": int,
                    },
                    validate_fun=self.check_exclude_months,
                    value=form.field_value("exclude_months"),
                    help_text="Comma-separated list of month numbers to exclude "
                    "from the count",
                ),
                FieldConfig(
                    name="include_from",
                    field_type=DayMonthWidget,
                    value={
                        "day": form.field_value("include_from_day"),
                        "month": form.field_value("include_from_month"),
                    },
                    help_text="Optional start date to include in the count",
                ),
                FieldConfig(
                    name="include_to",
                    field_type=DayMonthWidget,
                    value={
                        "day": form.field_value("include_to_day"),
                        "month": form.field_value("include_to_month"),
                    },
                    help_text="Optional end date to include in the count",
                ),
            ]
        }

        # parameter uses temporal_agg_func
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            additional_sections=additional_sections,
            agg_func_field_labels=TemporalWidgetField(
                label="Counter aggregation function",
                help_text="Aggregate the counter over time for each scenario "
                + "using the provided function",
            ),
            show_ignore_nan_field=True,
        )

    @staticmethod
    def check_exclude_months(
        name: str, label: str, values: list[int] | None
    ) -> Validation:
        """
        Checks that the exclude_months list contains valid month numbers.
        :param name: The field name.
        :param label: The field label.
        :param values: The field values.
        :return: The validation instance.
        """
        if values and not all([1 <= m <= 12 for m in values]):
            return Validation("The month numbers are not valid")
        return Validation()
