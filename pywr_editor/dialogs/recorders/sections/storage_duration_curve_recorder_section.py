from pywr_editor.form import StoragePickerWidget, TableValuesWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_flow_duration_curve_recorder_section import (
    AbstractFlowDurationCurveRecorderSection,
)
from .abstract_numpy_recorder_section import (
    AbstractNumpyRecorderSection,
    TemporalWidgetField,
)


class StorageDurationCurveRecorderSection(AbstractNumpyRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a StorageDurationCurveRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "node",
                "label": "Storage node",
                "field_type": StoragePickerWidget,
                "value": form.get_recorder_dict_value("node"),
                "help_text": "For each scenarios, this calculates the storage duration "
                "curve of the node provided above",
            },
            {
                "name": "percentiles",
                "field_type": TableValuesWidget,
                "field_args": {
                    "min_total_values": 2,
                    "lower_bound": 0,
                    "upper_bound": 100,
                    "enforce_bounds": True,
                    "use_integers_only": True,
                    "show_row_numbers": True,
                    "row_number_label": "Percentile index",
                },
                "validate_fun": AbstractFlowDurationCurveRecorderSection.check_percentiles,  # noqa: E501
                "value": {"values": form.get_recorder_dict_value("percentiles")},
                "help_text": "The percentiles (between 0 and 100) to use in the "
                + "calculation of the storage duration curve",
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            agg_func_field_labels=TemporalWidgetField(
                label="Percentile aggregation function",
                help_text="Aggregate the storage across percentiles for each scenario "
                + " using the provided function",
            ),
            show_ignore_nan_field=True,
            log_name=self.__class__.__name__,
        )

    def filter(self, form_data: dict) -> None:
        """
        Unpacks the values from the TableValuesWidget.
        :param form_data: The form dictionary.
        :return: None
        """
        # field is mandatory
        form_data["percentiles"] = form_data["percentiles"]["values"]
