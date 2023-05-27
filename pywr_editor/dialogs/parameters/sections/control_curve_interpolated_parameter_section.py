from ..parameter_dialog_form import ParameterDialogForm
from .abstract_control_curve_parameter_section import (
    AbstractControlCurveParameterSection,
)


class ControlCurveInterpolatedParameterSection(AbstractControlCurveParameterSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a ControlCurveInterpolatedParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            log_name=self.__class__.__name__,
            values_size_increment=2,
            additional_help_text=". The final value is linearly interpolated between "
            "control curves",
        )
