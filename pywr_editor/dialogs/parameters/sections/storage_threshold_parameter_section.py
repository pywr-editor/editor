from pywr_editor.form import StoragePickerWidget

from ..parameter_dialog_form import ParameterDialogForm
from .abstract_threshold_parameter_section import (
    AbstractThresholdParameterSection,
    ValueDict,
)


class StorageThresholdParameterSection(AbstractThresholdParameterSection):
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
                key="storage_node",
                widget=StoragePickerWidget,
            ),
            threshold_description="Compare the storage, from the node specified "
            + "below, against this threshold",
            value_rel_symbol_description="storage",
        )
