from ..parameter_dialog_form import ParameterDialogForm
from .abstract_annual_profile_parameter_section import (
    AbstractAnnualProfileParameterSection,
)
from pywr_editor.form import (
    InterpDayWidget,
    MonthlyValuesWidget,
    OptMonthlyBoundsWidget,
)


class MonthlyProfileParameterSection(AbstractAnnualProfileParameterSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a monthly profile parameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        self.form: ParameterDialogForm
        # noinspection PyTypeChecker
        super().__init__(
            form=form,
            section_data=section_data,
            values_widget=MonthlyValuesWidget,
            opt_widget=OptMonthlyBoundsWidget,
            log_name=self.__class__.__name__,
        )

        # Add interp_day option
        self.form_dict["Miscellaneous"].insert(
            0,
            {
                "name": "interp_day",
                "label": "Interpolation",
                "field_type": InterpDayWidget,
                "value": self.form.get_param_dict_value("interp_day"),
                "help_text": "When None, the series is a piecewise monthly profile "
                + "otherwise the series is interpolated. With 'First day' the 12 "
                + "values represent the first day of each month. With 'Last day' "
                + "the 12 values represent instead the last day of each month",
            },
        )
