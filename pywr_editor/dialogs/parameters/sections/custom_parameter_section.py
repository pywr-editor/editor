from ..parameter_dialog_form import ParameterDialogForm
from pywr_editor.form import AbstractCustomComponentSection

"""
 This section allows setting up a custom parameter dictionary
 by providing key/value pairs with support to external files
 (to configure url, table, index_col, etc. fields)
"""


class CustomParameterSection(AbstractCustomComponentSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a custom parameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form, section_data=section_data, component_type="parameter"
        )
