from pywr_editor.form import FieldConfig, FloatWidget, ParameterLineEditWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection


class TotalParameterRecorderSection(AbstractRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a TotalParameterRecorder.
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
                    help_text="Store the parameter's mean value at the end of "
                    "the simulation for each scenario",
                ),
                FieldConfig(
                    name="factor",
                    field_type=FloatWidget,
                    default_value=1,
                    value=form.field_value("factor"),
                    help_text="Scale the parameter values by the provided factor",
                ),
                FieldConfig(
                    name="integrate",
                    field_type="boolean",
                    default_value=False,
                    value=form.field_value("integrate"),
                    help_text="Integrate the parameter values over time (i.e. this "
                    "multiplies the values by the time-step length in days)",
                ),
            ],
        )
