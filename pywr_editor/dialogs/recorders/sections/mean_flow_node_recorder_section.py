from pywr_editor.form import FieldConfig, NodePickerWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class MeanFlowNodeRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a MeanFlowNodeRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            FieldConfig(
                name="node",
                field_type=NodePickerWidget,
                value=form.field_value("node"),
                help_text="Store the mean flow through the node provided above "
                "for each scenario",
            )
        ]
        super().__init__(form=form, section_data=section_data, section_fields=fields)
