from pywr_editor.form import FloatWidget, NodePickerWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_numpy_recorder_section import (
    AbstractNumpyRecorderSection,
    TemporalWidgetField,
)


class NumpyArrayNodeSuppliedRatioRecorderSection(AbstractNumpyRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a NumpyArrayNodeSuppliedRatioRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "node",
                "field_type": NodePickerWidget,
                "value": form.get_recorder_dict_value("node"),
                "help_text": "Store the node's supply ratio in a numpy array during "
                + "the simulation for each scenario. The ratio is defined as the "
                + "actual node flow divided by its maximum flow",
            },
            {
                "name": "factor",
                "field_type": FloatWidget,
                "default_value": 1,
                "value": form.get_recorder_dict_value("factor"),
                "help_text": "Scale the ratio by the provided factor",
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            agg_func_field_labels=TemporalWidgetField(
                help_text="Aggregate the flow over time for each scenario using the "
                + "provided function"
            ),
            log_name=self.__class__.__name__,
        )
