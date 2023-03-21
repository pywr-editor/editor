from ..parameter_dialog_form import ParameterDialogForm
from .abstract_threshold_parameter_section import (
    AbstractThresholdParameterSection,
)


class CurrentYearThresholdParameterSection(AbstractThresholdParameterSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a CurrentYearThresholdParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            log_name=self.__class__.__name__,
            threshold_description="Returns one of two values depending on the year of "
            + "the current timestep",
            value_rel_symbol_description="current year",
        )
