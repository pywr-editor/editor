from pywr_editor.form import FieldConfig, TableValuesWidget, Validation

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_flow_duration_curve_recorder_section import (
    AbstractFlowDurationCurveRecorderSection,
)


class SeasonalFlowDurationCurveRecorderSection(
    AbstractFlowDurationCurveRecorderSection
):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a SeasonalFlowDurationCurveRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=[
                FieldConfig(
                    name="months",
                    value={"values": form.field_value("months")},
                    field_type=TableValuesWidget,
                    field_args={
                        "min_total_values": 1,
                        "lower_bound": 1,
                        "upper_bound": 12,
                        "use_integers_only": True,
                    },
                    validate_fun=self.check_months,
                    help_text="The numeric values of the months the flow duration "
                    "curve should be calculated for",
                ),
            ],
            additional_fdc_help_text=". The FDC will be calculated only for the "
            + "months provided below",
        )

    @staticmethod
    def check_months(
        name: str, label: str, values: dict[str, list[float]]
    ) -> Validation:
        """
        Checks that the months are all different.
        :param name: The field name.
        :param label: The field name.
        :param values: The percentiles.
        :return: The form validation instance.
        """
        v = values["values"]
        if len(set(v)) != len(v):
            return Validation("The months must be unique numbers")
        return Validation()

    def filter(self, form_data: dict) -> None:
        """
        Unpacks the months array.
        :param form_data: The form dictionary.
        :return: None
        """
        super().filter(form_data)
        form_data["months"] = form_data["months"]["values"]
