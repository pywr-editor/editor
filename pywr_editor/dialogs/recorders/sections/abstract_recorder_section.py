from pywr_editor.form import FormSection

from ..recorder_dialog_form import RecorderDialogForm

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
        """
        super().__init__(form, section_data)
        if additional_sections is None:
            additional_sections = {}

        self.add_fields(
            {
                "Configuration": section_fields + [form.comment],
                **additional_sections,
                **form.optimisation_section,
            }
        )
