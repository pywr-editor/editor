from pywr_editor.form import FieldConfig, NodePickerWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class DeficitFrequencyNodeRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a DeficitFrequencyNodeRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            FieldConfig(
                name="node",
                field_type=NodePickerWidget,
                value=form.field_value("node"),
                help_text="Store the deficit frequency of the node provide above "
                "for each scenario. A deficit is recorded when the node's flow is "
                "less than its maximum. The frequency is defined as the number of "
                "time-steps with a deficit divided by the number of modelled "
                "time-steps",
            ),
        ]
        super().__init__(form=form, section_data=section_data, section_fields=fields)
