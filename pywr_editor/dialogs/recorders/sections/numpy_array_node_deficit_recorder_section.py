from pywr_editor.form import FieldConfig, FloatWidget, NodePickerWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_numpy_recorder_section import (
    AbstractNumpyRecorderSection,
    TemporalWidgetField,
)


class NumpyArrayNodeDeficitRecorderSection(AbstractNumpyRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a NumpyArrayNodeDeficitRecorder.
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
                    help_text="Store the node's deficit in a numpy array during "
                    "the simulation for each scenario. The deficit is defined as "
                    "the difference between the node's max flow and the actual flow",
                ),
                FieldConfig(
                    name="factor",
                    field_type=FloatWidget,
                    default_value=1,
                    field_args={"min_value": 0},
                    value=form.field_value("factor"),
                    help_text="Scale the deficit by the provided factor",
                ),
            ],
            agg_func_field_labels=TemporalWidgetField(
                help_text="Aggregate the flow over time for each scenario using the "
                + "provided function"
            ),
        )
