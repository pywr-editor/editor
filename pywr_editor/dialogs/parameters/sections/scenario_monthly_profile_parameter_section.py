from ..parameter_dialog_form import ParameterDialogForm
from .abstract_scenario_profile_parameter_section import (
    AbstractScenarioProfileParameterSection,
)


class ScenarioMonthlyProfileParameterSection(
    AbstractScenarioProfileParameterSection
):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a ScenarioMonthlyProfileParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            profile_type="monthly",
            log_name=self.__class__.__name__,
        )
