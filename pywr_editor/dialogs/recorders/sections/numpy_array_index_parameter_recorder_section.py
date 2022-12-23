from pywr_editor.form import ParameterLineEditWidget

from ..recorder_dialog_form import RecorderDialogForm
from .abstract_numpy_recorder_section import (
    AbstractNumpyRecorderSection,
    TemporalWidgetField,
)


class NumpyArrayIndexParameterRecorderSection(AbstractNumpyRecorderSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a NumpyArrayIndexParameterRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        fields = [
            {
                "name": "parameter",
                "field_type": ParameterLineEditWidget,
                "field_args": {
                    "include_param_key": form.model_config.pywr_parameter_data.get_keys_with_parent_class(  # noqa: E501
                        "IndexParameter"
                    )
                    + form.model_config.includes.get_keys_with_subclass(
                        "IndexParameter", "parameter"
                    ),
                },
                "value": form.get_recorder_dict_value("parameter"),
                "help_text": "Store the parameter's value in a numpy array during "
                + "the simulation for each scenario",
            },
        ]
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=fields,
            agg_func_field_labels=TemporalWidgetField(
                help_text="Aggregate the index parameter's value over time for each "
                + "scenario using the provided function"
            ),
            log_name=self.__class__.__name__,
        )
