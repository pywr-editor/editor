from ..recorder_dialog_form import RecorderDialogForm
from pywr_editor.form import FormSection
from pywr_editor.utils import Logging

"""
 Defines a generic section for a recorder. This holds and handles
 the optimisation fields.
"""


class AbstractRecorderSection(FormSection):
    def __init__(
        self,
        form: RecorderDialogForm,
        section_data: dict,
        section_fields: list[dict],
        log_name: str,
        additional_sections: dict[str, list[dict]] | None = None,
    ):
        """
        Initialises the form section for a recorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param section_fields: A list containing the fields to add to the
        section.
        :param additional_sections: Additional lists of sections to add to the
        section. This is must be a dictionary with the section title as key
        and list of fields as values. The sections will be added after the
        "Configuration" section but before the "Optimisation" section.
        :param log_name: The name of the log.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(log_name)
        self.section_fields = section_fields
        self.additional_sections = additional_sections
        if self.additional_sections is None:
            self.additional_sections = {}

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.form: RecorderDialogForm
        self.logger.debug("Registering form")

        data_dict = {
            "Configuration": self.section_fields
            + [
                self.form.comment,
            ],
            **self.additional_sections,
            **self.form.optimisation_section,
        }

        return data_dict
