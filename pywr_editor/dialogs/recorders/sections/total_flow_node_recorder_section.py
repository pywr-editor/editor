from pywr_editor.form import FieldConfig, FloatWidget, NodePickerWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class TotalFlowNodeRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a TotalFlowNodeRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=[
                FieldConfig(
                    name="node",
                    field_type=NodePickerWidget,
                    value=form.field_value("node"),
                    help_text="Store the total flow through the node provided above "
                    "for each scenario",
                ),
                FieldConfig(
                    name="factor",
                    field_type=FloatWidget,
                    field_args={"min_value": 0},
                    default_value=1,
                    value=form.field_value("factor"),
                    help_text="Scale the volume by the provided factor (e.g. for "
                    "calculating operational costs)",
                ),
            ],
        )
