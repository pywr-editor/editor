from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection
from pywr_editor.form import (
    RecorderAggFuncWidget,
    RecordersListPickerWidget,
)


class AggregatedRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a AggregatedRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "recorders",
                "field_type": RecordersListPickerWidget,
                "value": form.get_recorder_dict_value("recorders"),
                "help_text": "The recorder aggregates the recorders' values using the "
                + "aggregation function specified below",
            },
            {
                "name": "recorder_agg_func",
                "label": "Recorder aggregation function",
                "field_type": RecorderAggFuncWidget,
                "value": {
                    "recorder_agg_func": form.get_recorder_dict_value(
                        "recorder_agg_func"
                    ),
                    "agg_func": form.get_recorder_dict_value("agg_func"),
                },
                "help_text": "If you select 'Use scenario aggregation function', note "
                + "that only the functions listed above are supported by the "
                + " aggregation. For example, if the scenario aggregation is set to "
                + "'Percentile', the recorder will throw an error",
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            log_name=self.__class__.__name__,
        )
