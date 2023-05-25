from pywr_editor.form import FieldConfig, ParameterLineEditWidget, StoragePickerWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_numpy_recorder_section import (
    AbstractNumpyRecorderSection,
    TemporalWidgetField,
)


class NumpyArrayNormalisedStorageRecorderSection(AbstractNumpyRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a NumpyArrayNormalisedStorageRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=[
                FieldConfig(
                    name="node",
                    label="Storage node",
                    field_type=StoragePickerWidget,
                    value=form.field_value("node"),
                    help_text="For each scenario and time-step, this stores the node's "
                    "normalised storage. The volume is normalised using the control "
                    "curve parameter provided below such that the recorder's values of "
                    "1 , 0 and -1 align with full, at control curve and empty volume"
                    "respectively",
                ),
                FieldConfig(
                    name="parameter",
                    label="Control curve parameter",
                    field_type=ParameterLineEditWidget,
                    field_args={
                        "include_param_key": form.model_config.pywr_parameter_data.keys_with_parent_class(  # noqa: E501
                            "BaseControlCurveParameter"
                        )
                        + form.model_config.includes.get_keys_with_subclass(
                            "BaseControlCurveParameter", "parameter"
                        ),
                    },
                    value=form.field_value("parameter"),
                ),
            ],
            agg_func_field_labels=TemporalWidgetField(
                help_text="Aggregate the normalised storage over time for each "
                "scenario using the provided function"
            ),
            show_ignore_nan_field=True,
        )
