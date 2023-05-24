from pywr_editor.form import FieldConfig, FormSection, ParameterLineEditWidget
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class DivisionParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a DivisionParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(self.__class__.__name__)

        self.form: ParameterDialogForm
        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="numerator",
                        field_type=ParameterLineEditWidget,
                        value=self.form.field_value("numerator"),
                        help_text="The parameter to use as the numerator",
                    ),
                    FieldConfig(
                        name="denominator",
                        field_type=ParameterLineEditWidget,
                        value=self.form.field_value("parameters"),
                        help_text="The parameter to use as the denominator",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )
