from ..parameter_dialog_form import ParameterDialogForm
from .abstract_min_max_parameter_section import AbstractMinMaxParameterSection


class NegativeMinParameterSection(AbstractMinMaxParameterSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a NegativeMinParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            log_name=self.__class__.__name__,
            parameter_help_text="Take the minimum between the negative value of the "
            + "provided parameter and the threshold below",
        )
