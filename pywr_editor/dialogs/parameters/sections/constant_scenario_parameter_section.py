from pywr_editor.form import TableValuesWidget

from ..parameter_dialog_form import ParameterDialogForm
from .abstract_constant_scenario_parameter_section import (
    AbstractConstantScenarioParameterSection,
)


class ConstantScenarioParameterSection(AbstractConstantScenarioParameterSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a ConstantScenarioParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        # get scenario size for initial requirement check
        scenario_name = form.field_value("scenario")
        scenarios = form.model_config.scenarios

        exact_total_values = None
        if isinstance(scenario_name, str) and scenarios.exists(scenario_name):
            exact_total_values = scenarios.config(scenario_name, as_dict=False).size

        super().__init__(
            form=form,
            section_data=section_data,
            values_widget=TableValuesWidget,
            values_widget_options={
                "show_row_numbers": True,
                "row_number_label": "Ensemble number",
                "exact_total_values": exact_total_values,
            },
            log_name=self.__class__.__name__,
        )
