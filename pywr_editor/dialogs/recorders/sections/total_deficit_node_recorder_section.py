from pywr_editor.form import NodePickerWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class TotalDeficitNodeRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a TotalDeficitNodeRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "node",
                "field_type": NodePickerWidget,
                "value": form.get_recorder_dict_value("node"),
                "help_text": "Store the total the difference between modelled flow "
                + "and the maximum flow for the node provided above for each scenario",
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            log_name=self.__class__.__name__,
        )
