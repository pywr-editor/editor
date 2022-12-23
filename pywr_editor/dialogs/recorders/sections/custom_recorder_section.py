from pywr_editor.form import AbstractCustomComponentSection

from ..recorder_dialog_form import RecorderDialogForm

"""
 This section allows setting up a custom recorder dictionary
 by providing key/value pairs with support to external files
 (to configure url, table, index_col, etc. fields)
"""


class CustomRecorderSection(AbstractCustomComponentSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for a custom recorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        # disable optimisation section
        if section_data["enable_optimisation_section"] is False:
            additional_sections = {}
        else:
            additional_sections = form.optimisation_section

        super().__init__(
            form=form,
            section_data=section_data,
            component_type="recorder",
            additional_sections=additional_sections,
        )
