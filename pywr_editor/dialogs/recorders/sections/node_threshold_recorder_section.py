from pywr_editor.form import NodePickerWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_threshold_recorder_section import AbstractThresholdRecorderSection


class NodeThresholdRecorderSection(AbstractThresholdRecorderSection):
    def __init__(
        self,
        form: RecorderDialogForm,
        section_data: dict,
    ):
        """
        Initialises the form section for NodeThresholdRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            log_name=self.__class__.__name__,
            node_widget=NodePickerWidget,
        )
