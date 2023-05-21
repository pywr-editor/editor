from pywr_editor.form import FormValidation, NodePickerWidget, TableValuesWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_numpy_recorder_section import (
    AbstractNumpyRecorderSection,
    TemporalWidgetField,
)


class AbstractFlowDurationCurveRecorderSection(AbstractNumpyRecorderSection):
    def __init__(
        self,
        form: RecorderDialogForm,
        section_data: dict,
        section_fields: list[dict],
        log_name: str,
        additional_fdc_help_text: str = "",
    ):
        """
        Initialises the form section for a recorder calculating a FDC.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param section_fields: A list containing the fields to append to the
        section.
        :param log_name: The name of the log.
        :param additional_fdc_help_text: Additional text to append to the description
        of the FDC calculation.
        """
        fields = [
            {
                "name": "node",
                "field_type": NodePickerWidget,
                "value": form.get_recorder_dict_value("node"),
                "help_text": "Calculates the flow duration curve using the flow "
                + "of the node provided above for each scenario",
            },
            {
                "name": "percentiles",
                "field_type": TableValuesWidget,
                "field_args": {
                    "min_total_values": 2,
                    "lower_bound": 0,
                    "upper_bound": 100,
                    "use_integers_only": True,
                    "show_row_numbers": True,
                    "row_number_label": "Percentile index",
                },
                "validate_fun": self.check_percentiles,
                "value": {"values": form.get_recorder_dict_value("percentiles")},
                "help_text": "The percentiles (between 0 and 100) to use in the "
                + "calculation of the flow duration curve"
                + additional_fdc_help_text,
            },
        ] + section_fields

        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            agg_func_field_labels=TemporalWidgetField(
                label="Percentile aggregation function",
                help_text="Aggregate the flow duration values across percentiles "
                + "for each scenario using the provided function",
            ),
            show_ignore_nan_field=True,
            log_name=log_name,
        )

    @staticmethod
    def check_percentiles(
        name: str, label: str, values: dict[str, list[int]]
    ) -> FormValidation:
        """
        Checks that the percentiles are all different.
        :param name: The field name.
        :param label: The field name.
        :param values: The percentiles.
        :return: The form validation instance.
        """
        v = values["values"]
        if len(set(v)) != len(v):
            return FormValidation(
                validation=False, error_message="The percentiles must be unique"
            )
        return FormValidation(validation=True)

    def filter(self, form_data: dict) -> None:
        """
        Unpacks the percentiles.
        :param form_data: The form dictionary.
        :return: None
        """
        # field is mandatory
        form_data["percentiles"] = form_data["percentiles"]["values"]
