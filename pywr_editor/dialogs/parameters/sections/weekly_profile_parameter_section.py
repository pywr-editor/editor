from pywr_editor.form import OptWeeklyBoundsWidget, WeeklyValuesWidget

from ..parameter_dialog_form import ParameterDialogForm
from .abstract_annual_profile_parameter_section import (
    AbstractAnnualProfileParameterSection,
)


class WeeklyProfileParameterSection(AbstractAnnualProfileParameterSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a weekly profile parameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        # noinspection PyTypeChecker
        super().__init__(
            form=form,
            section_data=section_data,
            values_widget=WeeklyValuesWidget,
            opt_widget=OptWeeklyBoundsWidget,
            log_name=self.__class__.__name__,
        )
