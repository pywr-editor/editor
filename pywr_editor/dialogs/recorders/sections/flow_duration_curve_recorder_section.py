from ..recorder_dialog_form import RecorderDialogForm
from .abstract_flow_duration_curve_recorder_section import (
    AbstractFlowDurationCurveRecorderSection,
)


class FlowDurationCurveRecorderSection(AbstractFlowDurationCurveRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a FlowDurationCurveRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=[],
            log_name=self.__class__.__name__,
        )
