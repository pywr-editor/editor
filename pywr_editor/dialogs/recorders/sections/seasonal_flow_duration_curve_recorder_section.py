from ..recorder_dialog_form import RecorderDialogForm
from .abstract_flow_duration_curve_recorder_section import (
    AbstractFlowDurationCurveRecorderSection,
)
from pywr_editor.form import TableValuesWidget, FormValidation


class SeasonalFlowDurationCurveRecorderSection(
    AbstractFlowDurationCurveRecorderSection
):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a SeasonalFlowDurationCurveRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        section_fields = [
            {
                "name": "months",
                "value": {"values": form.get_recorder_dict_value("months")},
                "field_type": TableValuesWidget,
                "field_args": {
                    "min_total_values": 1,
                    "lower_bound": 1,
                    "upper_bound": 12,
                    "use_integers_only": True,
                },
                "validate_fun": self.check_months,
                "help_text": "The numeric values of the months the flow duration "
                + "curve should be calculated for",
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=section_fields,
            log_name=self.__class__.__name__,
            additional_fdc_help_text=". The FDC will be calculated only for the "
            + "months provided below",
        )

    @staticmethod
    def check_months(name: set, label: str, values: dict[str, list[float]]):
        """
        Checks that the months are all different.
        :param name: The field name.
        :param label: The field name.
        :param values: The percentiles.
        :return: The form validation instance.
        """
        v = values["values"]
        if len(set(v)) != len(v):
            return FormValidation(
                validation=False,
                error_message="The months must be unique numbers",
            )
        return FormValidation(validation=True)

    def filter(self, form_data: dict) -> None:
        """
        Unpacks the months array.
        :param form_data: The form dictionary.
        :return: None
        """
        super().filter(form_data)
        form_data["months"] = form_data["months"]["values"]
