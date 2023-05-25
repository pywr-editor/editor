from pywr_editor.form import (
    EventDurationAggFuncWidget,
    FieldConfig,
    RecorderLineEditWidget,
)

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class EventDurationRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a EventDurationRecorder.
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
                help_text="Aggregate the duration of the events stored by the "
                "Event recorder using the aggregation function provided below",
            ),
            FieldConfig(
                name="recorder_agg_func",
                label="Duration aggregation function",
                field_type=EventDurationAggFuncWidget,
                value={
                    "recorder_agg_func": form.field_value("recorder_agg_func"),
                    "agg_func": form.field_value("agg_func"),
                },
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
