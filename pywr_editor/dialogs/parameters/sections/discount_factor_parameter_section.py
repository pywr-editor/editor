from pywr_editor.form import (
    FieldConfig,
    FloatWidget,
    FormSection,
    IntegerWidget,
    Validation,
)

from ..parameter_dialog_form import ParameterDialogForm


class DiscountFactorParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a DiscountFactorParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="discount_rate",
                        field_type=FloatWidget,
                        value=self.form.field_value("discount_rate"),
                        allow_empty=False,
                        validate_fun=self._check_rate,
                        help_text="The parameter provides a discount factor for each "
                        "simulated year calculated as the inverse of "
                        "(1+ Discount rate)^(Year - Base year). The rate must be a "
                        "number between 0 and 1",
                    ),
                    FieldConfig(
                        name="base_year",
                        field_type=IntegerWidget,
                        default_value=0,
                        value=self.form.field_value("base_year"),
                        allow_empty=False,
                        help_text="Base year (i.e. the year with a discount rate "
                        "equal to 1)",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )

    @staticmethod
    def _check_rate(name: str, label: str, value: int) -> Validation:
        """
        Checks that discount rate is between 0 and 1.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The validation instance.
        """
        # ignore when value is 0
        if not 0 <= value <= 1:
            return Validation("The number must be between 0 and 1")

        return Validation()
