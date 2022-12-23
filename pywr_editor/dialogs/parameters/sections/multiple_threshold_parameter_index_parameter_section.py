from pywr_editor.form import ModelParameterPickerWidget

from ..parameter_dialog_form import ParameterDialogForm
from .abstract_threshold_parameter_section import ValueDict
from .abstract_thresholds_parameter_section import (
    AbstractThresholdsParameterSection,
)


class MultipleThresholdParameterIndexParameterSection(
    AbstractThresholdsParameterSection
):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a MultipleThresholdParameterIndexParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            log_name=self.__class__.__name__,
            value_dict=ValueDict(
                key="parameter",
                widget=ModelParameterPickerWidget,
                help_text="Compare the thresholds against the value of the parameter "
                + "provided above at each timestep. This parameter returns a zero-"
                + "based index. For example, if only one threshold is provided, the "
                + "index can be 0 (above threshold) or 1 (below threshold). For two "
                + "thresholds the index can be either 0  (above both), 1 (in between),"
                + " or 2 (below both)",
            ),
        )
