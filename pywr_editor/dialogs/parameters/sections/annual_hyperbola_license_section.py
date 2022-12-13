from ..parameter_dialog_form import ParameterDialogForm
from .abstract_storage_license_section import AbstractStorageLicenseSection
from pywr_editor.form import FloatWidget


class AnnualHyperbolaLicenseSection(AbstractStorageLicenseSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for am AnnualHyperbolaLicense.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            log_name=self.__class__.__name__,
            amount_help_text="At each time step the parameter returns the following "
            + "value: <i>Scale factor</i> / <i>x</i>, where<i>x</i> = "
            + "[(<i>License amount</i> - <i>Used volume</i>) / (365 - <i>d</i>)] "
            + "/ (<i>License amount</i> / 365), <i>Used volume</i> is the volume "
            + "through the node, from the beginning of the simulation to the current "
            + "the day of the year <i>d</i> and <i>Scale factor</i> the scale factor "
            + "in the hyperbola function",
            additional_fields=[
                {
                    "name": "value",
                    "label": "Scaling factor",
                    "field_type": FloatWidget,
                    "allow_empty": False,
                    "value": form.get_param_dict_value("value"),
                    "help_text": "The scaling factor used in the hyperbola function",
                },
            ],
        )
