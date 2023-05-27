from pywr_editor.form import (
    FieldConfig,
    FloatWidget,
    FormSection,
    ParameterLineEditWidget,
)

from ..parameter_dialog_form import ParameterDialogForm

"""
 Abstract class for MinParameter, MaxParameter,
 NegativeMinParameter and NegativeMaxParameter.
"""


class OffsetParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for the OffsetParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="parameter",
                        field_type=ParameterLineEditWidget,
                        value=self.form.field_value("parameter"),
                        help_text="Offset this parameter value by the constant offset "
                        "provided below",
                    ),
                    FieldConfig(
                        name="offset",
                        field_type=FloatWidget,
                        # pywr class defaults to 0
                        default_value=0,
                        allow_empty=False,
                        value=self.form.field_value("offset"),
                        help_text="Apply this offset to the above parameter. "
                        "Default to 0",
                    ),
                ],
                self.form.optimisation_config_group_name: [
                    self.form.is_variable_field,
                    FieldConfig(
                        name="lower_bounds",
                        field_type=FloatWidget,
                        value=self.form.field_value("lower_bounds"),
                        help_text="The smallest value for the parameter during "
                        "optimisation",
                    ),
                    FieldConfig(
                        name="upper_bounds",
                        field_type=FloatWidget,
                        value=self.form.field_value("upper_bounds"),
                        help_text="The largest value for the parameter during "
                        "optimisation",
                    ),
                ],
            }
        )

        # disable optimisation section
        if self.section_data["enable_optimisation_section"] is False:
            del self.fields_[self.form.optimisation_config_group_name]
