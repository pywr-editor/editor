from ..parameter_dialog_form import ParameterDialogForm
from .abstract_storage_license_section import AbstractStorageLicenseSection


class AnnualLicenseSection(AbstractStorageLicenseSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for an AnnualLicense.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            log_name=self.__class__.__name__,
            amount_help_text="The amount available at each time step is calculated as: "
            "(<i>License amount</i> - <i>Used volume by node</i> * <i>&Delta;t</i>) "
            "/ (<i>Remaining days in year</i> * <i>&Delta;t</i>), where "
            "<i>&Delta;t</i> is the timestep length",
        )
