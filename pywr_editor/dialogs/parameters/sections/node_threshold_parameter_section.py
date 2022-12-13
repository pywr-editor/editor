from ..parameter_dialog_form import ParameterDialogForm
from .abstract_threshold_parameter_section import (
    AbstractThresholdParameterSection,
    ValueDict,
)
from pywr_editor.form import NodePickerWidget


class NodeThresholdParameterSection(AbstractThresholdParameterSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a StorageThresholdParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            log_name=self.__class__.__name__,
            value_dict=ValueDict(
                key="node",
                widget=NodePickerWidget,
            ),
            threshold_description="Compare the flow values of the node specified below "
            + "against this threshold",
        )
