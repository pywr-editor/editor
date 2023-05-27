from pywr_editor.form import (
    EventTrackedParameterAggFuncWidget,
    EventTypeWidget,
    FieldConfig,
    IntegerWidget,
    ParameterLineEditWidget,
    RecorderLineEditWidget,
)

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class EventRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a EventRecorder. The recorder stores Event
        objects every time a parameter or recorder value is above 0 for a certain
        period of time.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            FieldConfig(
                name="threshold_type",
                field_type=EventTypeWidget,
                value=form.field_value("threshold"),
                help_text="The type of model component whose value defines when "
                "the events are triggered. When the value of the component provided "
                "below is larger than zero, the recorder stores a new Even object "
                "containing information when the event started and ended",
            ),
            FieldConfig(
                name="threshold_parameter",
                label="Parameter",
                field_type=ParameterLineEditWidget,
                value=form.field_value("threshold"),
                help_text="Use a parameter to define the event threshold. A new "
                "event is stored by this recorder when the parameter returns a value "
                "larger than zero",
            ),
            FieldConfig(
                name="threshold_recorder",
                label="Recorder",
                field_type=RecorderLineEditWidget,
                value=form.field_value("threshold"),
                help_text="Use a recorder to define the event threshold. A new "
                "event is stored by this recorder when the recorder above returns a "
                "value larger than zero",
            ),
            FieldConfig(
                name="minimum_event_length",
                field_type=IntegerWidget,
                field_args={
                    "min_value": 1,
                    "max_value": form.model_config.number_of_steps,
                },
                default_value=1,
                value=form.field_value("minimum_event_length"),
                help_text="The minimum number of time-steps that the event must "
                "last for to be recorded. Default to 1",
            ),
        ]
        additional_sections = {
            "Parameter tracking": [
                FieldConfig(
                    name="tracked_parameter",
                    field_type=ParameterLineEditWidget,
                    field_args={"is_mandatory": False},
                    value=form.field_value("tracked_parameter"),
                    help_text="For each scenario, the recorder stores the value of "
                    "the parameter specified above when the event is active",
                ),
                FieldConfig(
                    name="event_agg_func",
                    label="Tracked parameter aggregation function",
                    field_type=EventTrackedParameterAggFuncWidget,
                    value={
                        "event_agg_func": form.field_value("event_agg_func"),
                        "agg_func": form.field_value("agg_func"),
                    },
                    help_text="When provided, the recorder stores the aggregated "
                    "values of the tracked parameter in the final DataFrame, using "
                    "the aggregation function specified above. This is optional",
                ),
            ]
        }
        super().__init__(
            form=form,
            section_data=section_data,
            additional_sections=additional_sections,
            section_fields=fields,
        )

    def filter(self, form_data: dict) -> None:
        """
        Gets the threshold value depending on the selected type.
        :param form_data: The form data.
        :return: None
        """
        self.form.find_field("threshold_type").widget.store_threshold(form_data)
