from pywr_editor.form import FieldConfig, ParameterLineEditWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_numpy_recorder_section import (
    AbstractNumpyRecorderSection,
    TemporalWidgetField,
)


class NumpyArrayDailyProfileParameterRecorderSection(AbstractNumpyRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a NumpyArrayDailyProfileParameterRecorder.
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
                    help_text="Store the daily profile, given by the specified "
                    "parameter, in a numpy array during the simulation for each "
                    "scenario",
                ),
            ],
            agg_func_field_labels=TemporalWidgetField(
                help_text="Aggregate the parameter's value over time for each "
                + "scenario using the provided function"
            ),
            show_ignore_nan_field=True,
        )
