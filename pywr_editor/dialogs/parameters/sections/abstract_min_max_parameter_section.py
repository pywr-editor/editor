from pywr_editor.form import (
    FieldConfig,
    FloatWidget,
    FormSection,
    ParameterLineEditWidget,
)
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm

"""
 Abstract class for MinParameter, MaxParameter,
 NegativeMinParameter and NegativeMaxParameter.
"""


class AbstractMinMaxParameterSection(FormSection):
    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict,
        parameter_help_text: str,
        log_name: str,
    ):
        """
        Initialises the form section.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param log_name: The name to use in the logger.
        :param parameter_help_text: The help text to show for the parameter field.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(log_name)
        self.parameter_help_text = parameter_help_text

        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="parameter",
                        field_type=ParameterLineEditWidget,
                        value=self.form.field_value("parameter"),
                        help_text=self.parameter_help_text,
                    ),
                    FieldConfig(
                        name="threshold",
                        field_type=FloatWidget,
                        # pywr class defaults to 0
                        default_value=0,
                        allow_empty=False,
                        value=self.form.field_value("threshold"),
                        help_text="The threshold to compare to the above parameter. "
                        "Default to 0",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )
