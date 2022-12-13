from ..parameter_dialog_form import ParameterDialogForm
from .abstract_threshold_parameter_section import (
    AbstractThresholdParameterSection,
)


class CurrentOrdinalDayThresholdParameterSection(
    AbstractThresholdParameterSection
):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a CurrentOrdinalDayThresholdParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            log_name=self.__class__.__name__,
            threshold_description="Returns one of two values depending on the "
            + "Gregorian ordinal of the date of the current timestep",
        )
