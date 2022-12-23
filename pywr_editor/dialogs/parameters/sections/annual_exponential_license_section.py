from pywr_editor.form import FloatWidget

from ..parameter_dialog_form import ParameterDialogForm
from .abstract_storage_license_section import AbstractStorageLicenseSection


class AnnualExponentialLicenseSection(AbstractStorageLicenseSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for an AnnualExponentialLicense.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            log_name=self.__class__.__name__,
            amount_help_text="At each time step the parameter returns the following "
            + "value: <i>Maximum value</i> * exp(-<i>x</i>/<i>k</i>), where "
            + "<i>Maximum value</i> is the starting value, <i>x</i> = "
            + "[(<i>License amount</i> - <i>Used volume</i>) / (365 - <i>d</i>)] "
            + "/ (<i>License amount</i> / 365), <i>Used volume</i> is the volume "
            + "through the node, from the beginning of the simulation to the current "
            + "the day of the year <i>d</i>, and <i>k</i> is the scale factor",
            additional_fields=[
                {
                    "name": "max_value",
                    "label": "Maximum value",
                    "field_type": FloatWidget,
                    "allow_empty": False,
                    "value": form.get_param_dict_value("max_value"),
                    "help_text": "The starting value of the exponential function "
                    + "(i.e. when <i>x</i>=0)",
                },
                {
                    "name": "k",
                    "label": "Scale factor (<i>k</i>)",
                    "field_type": FloatWidget,
                    "allow_empty": False,
                    "value": form.get_param_dict_value("k"),
                    "help_text": "The scale factor for the exponent of the "
                    + "exponential function.",
                },
            ],
        )
