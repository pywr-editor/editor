from pywr_editor.form import ParameterLineEditWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class RollingWindowParameterRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a RollingWindowParameterRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "parameter",
                "field_type": ParameterLineEditWidget,
                "value": form.get_recorder_dict_value("parameter"),
                "help_text": "For each scenario, store the parameter's rolling mean "
                + "over the number of time-steps provided below",
            },
            {
                "name": "window",
                "field_type": "integer",
                "default_value": 1,
                "max_value": form.model_config.number_of_steps,
                "value": form.get_recorder_dict_value("window"),
                "help_text": "The window length as number of time-steps",
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            log_name=self.__class__.__name__,
        )
