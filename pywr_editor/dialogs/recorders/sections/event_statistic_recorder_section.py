from pywr_editor.form import (
    EventStatisticAggFuncWidget,
    FieldConfig,
    RecorderLineEditWidget,
)

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class EventStatisticRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a EventStatisticRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        sub_class = "EventRecorder"
        fields = [
            FieldConfig(
                name="event_recorder",
                field_type=RecorderLineEditWidget,
                field_args={
                    "include_recorder_key": [
                        # get key for EventRecorder
                        form.model_config.pywr_recorder_data.lookup_key(sub_class)
                    ]
                    + form.model_config.includes.get_keys_with_subclass(
                        sub_class, "recorder"
                    ),
                },
                value=form.field_value("event_recorder"),
                help_text="Aggregate the values of the tracked parameter in the "
                "Event recorder using the aggregation functions provided below",
            ),
            FieldConfig(
                name="event_agg_func",
                label="Event aggregation function",
                field_type=EventStatisticAggFuncWidget,
                value={
                    "event_agg_func": form.field_value("event_agg_func"),
                    "agg_func": form.field_value("agg_func"),
                },
                help_text="For each scenario and event in the Event recorder, "
                "aggregate the values of the tracked parameter using the function "
                "provided above. The recorder derives one value for each event",
            ),
            FieldConfig(
                name="recorder_agg_func",
                label="Tracked parameter aggregation function",
                field_type=EventStatisticAggFuncWidget,
                value={
                    "recorder_agg_func": form.field_value("recorder_agg_func"),
                    "agg_func": form.field_value("agg_func"),
                },
                help_text="For each scenario aggregate the aggregated event values "
                + "of the tracked parameter using the function provided above. The "
                + "recorder derives one value for each scenario",
            ),
        ]

        super().__init__(form=form, section_data=section_data, section_fields=fields)

    def filter(self, form_data: dict) -> None:
        """
        Gets the threshold value depending on the selected type.
        :param form_data: The form data.
        :return: None
        """
        self.form.find_field("threshold_type").widget.store_threshold(form_data)
