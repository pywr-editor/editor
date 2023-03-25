from pywr_editor.form import StoragePickerWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class MinimumVolumeStorageRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a MinimumVolumeStorageRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "node",
                "label": "Storage node",
                "field_type": StoragePickerWidget,
                "value": form.get_recorder_dict_value("node"),
                "help_text": "Store the minimum volume of the storage node "
                + "provided above for each scenario at the end of the simulation",
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            log_name=self.__class__.__name__,
        )
