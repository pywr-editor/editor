from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection
from pywr_editor.form import StoragePickerWidget, FloatWidget


class MinimumThresholdVolumeStorageRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a MinimumThresholdVolumeStorageRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "storage",
                "label": "Storage node",
                "field_type": StoragePickerWidget,
                "value": form.get_recorder_dict_value("storage"),
                "help_text": "The recorder stores 1 if the volume of the storage "
                + " node is below the threshold provided below at any time-step during "
                + "the simulation for each scenario. Otherwise zero is returned.",
            },
            {
                "name": "threshold",
                "field_type": FloatWidget,
                "value": form.get_recorder_dict_value("threshold"),
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            log_name=self.__class__.__name__,
        )
