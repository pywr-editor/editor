from pywr_editor.form import FieldConfig, IntegerWidget, ParameterLineEditWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class RollingWindowParameterRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialise the form section for a RollingWindowParameterRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=[
                FieldConfig(
                    name="parameter",
                    field_type=ParameterLineEditWidget,
                    value=form.field_value("parameter"),
                    help_text="For each scenario, store the parameter's rolling mean "
                    "over the number of time-steps provided below",
                ),
                FieldConfig(
                    name="window",
                    field_type=IntegerWidget,
                    field_args={"max_value": form.model_config.number_of_steps},
                    default_value=1,
                    value=form.field_value("window"),
                    help_text="The window length as number of time-steps",
                ),
            ],
        )
