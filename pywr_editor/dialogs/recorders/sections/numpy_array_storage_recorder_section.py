from pywr_editor.form import StoragePickerWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_numpy_recorder_section import (
    AbstractNumpyRecorderSection,
    TemporalWidgetField,
)


class NumpyArrayStorageRecorderSection(AbstractNumpyRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a NumpyArrayStorageRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "node",
                "label": "Storage node",
                "field_type": StoragePickerWidget,
                "value": form.get_recorder_dict_value("node"),
                "help_text": "Store the node's storage in a numpy array during the "
                + "simulation for each scenario",
            },
            {
                "name": "proportional",
                "label": "Relative storage",
                "field_type": "boolean",
                "default_value": False,
                "value": form.get_recorder_dict_value("proportional"),
                "help_text": "When 'Yes' store the relative storage (between 0 and 1) "
                + "instead of the absolute value",
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            agg_func_field_labels=TemporalWidgetField(
                help_text="Aggregate the storage over time for each scenario using the "
                + "provided function"
            ),
            show_ignore_nan_field=True,
            log_name=self.__class__.__name__,
        )
