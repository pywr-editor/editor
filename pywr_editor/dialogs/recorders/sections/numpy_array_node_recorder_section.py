from ..recorder_dialog_form import RecorderDialogForm
from .abstract_numpy_recorder_section import (
    AbstractNumpyRecorderSection,
    TemporalWidgetField,
)
from pywr_editor.form import NodePickerWidget, FloatWidget


class NumpyArrayNodeRecorderSection(AbstractNumpyRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a NumpyArrayNodeRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "node",
                "field_type": NodePickerWidget,
                "value": form.get_recorder_dict_value("node"),
                "help_text": "Store the node's flow in a numpy array "
                + "during the simulation for each scenario",
            },
            {
                "name": "factor",
                "field_type": FloatWidget,
                "default_value": 1,
                "value": form.get_recorder_dict_value("factor"),
                "help_text": "Scale the flows by the provided factor (e.g. for "
                + "calculating operational costs)",
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
            show_ignore_nan_field=True,
            log_name=self.__class__.__name__,
        )
