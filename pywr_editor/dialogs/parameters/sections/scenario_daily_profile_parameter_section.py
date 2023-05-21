from ..parameter_dialog_form import ParameterDialogForm
from .abstract_scenario_profile_parameter_section import (
    AbstractScenarioProfileParameterSection,
)


class ScenarioDailyProfileParameterSection(AbstractScenarioProfileParameterSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a ScenarioDailyProfileParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            profile_type="daily",
            log_name=self.__class__.__name__,
        )
