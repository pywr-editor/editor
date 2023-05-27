from pywr_editor.form import StoragePickerWidget

from .abstract_threshold_recorder_section import AbstractThresholdRecorderSection


class StorageThresholdRecorderSection(AbstractThresholdRecorderSection):
    def __init__(self, form, section_data):
        """
        Initialises the form section for StorageThresholdRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form, section_data=section_data, node_widget=StoragePickerWidget
        )
