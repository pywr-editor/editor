from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection
from pywr_editor.form import ParameterLineEditWidget, FloatWidget


class TimestepCountIndexParameterRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a TimestepCountIndexParameterRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "parameter",
                "field_type": ParameterLineEditWidget,
                "value": form.get_recorder_dict_value("parameter"),
                "field_args": {
                    "include_param_key": form.model_config.pywr_parameter_data.get_keys_with_parent_class(  # noqa: E501
                        "IndexParameter"
                    )
                    + form.model_config.includes.get_keys_with_subclass(
                        "IndexParameter", "parameter"
                    ),
                },
                "help_text": "Store the number of time-steps the index parameter "
                + "exceeds the threshold provided below for each scenario",
            },
            {
                "name": "threshold",
                "field_type": FloatWidget,
                "value": form.get_recorder_dict_value("threshold"),
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            log_name=self.__class__.__name__,
        )
