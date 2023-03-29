from pywr_editor.form import FloatWidget, NodePickerWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class TotalFlowNodeRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a TotalFlowNodeRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "node",
                "field_type": NodePickerWidget,
                "value": form.get_recorder_dict_value("node"),
                "help_text": "Store the total flow through the node provided above "
                + "for each scenario",
            },
            {
                "name": "factor",
                "field_type": FloatWidget,
                "field_args": {"min_value": 0},
                "default_value": 1,
                "value": form.get_recorder_dict_value("factor"),
                "help_text": "Scale the volume by the provided factor (e.g. for "
                + "calculating operational costs)",
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            log_name=self.__class__.__name__,
        )
