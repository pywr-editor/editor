from pywr_editor.form import ModelRecorderPickerWidget

from ..parameter_dialog_form import ParameterDialogForm
from .abstract_threshold_parameter_section import (
    AbstractThresholdParameterSection,
    ValueDict,
)


class RecorderThresholdParameterSection(AbstractThresholdParameterSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a RecorderThresholdParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            log_name=self.__class__.__name__,
            value_dict=ValueDict(
                key="recorder",
                widget=ModelRecorderPickerWidget,
            ),
            threshold_description="Compare the values of the recorder the node "
            + "specified below against this threshold",
        )
