from ..recorder_dialog_form import RecorderDialogForm
from .abstract_hydropower_recorder_section import (
    AbstractHydropowerRecorderSection,
)


class HydropowerRecorderSection(AbstractHydropowerRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a HydropowerRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            node_help_text="For each scenario and time-step, the recorder "
            + "stores the hydropower production",
            log_name=self.__class__.__name__,
        )
