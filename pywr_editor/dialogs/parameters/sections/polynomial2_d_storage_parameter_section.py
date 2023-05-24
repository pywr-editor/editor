from pywr_editor.form import (
    FieldConfig,
    FloatWidget,
    FormSection,
    ParameterLineEditWidget,
    Polynomial2DCoefficientsWidget,
    StoragePickerWidget,
)

from ..parameter_dialog_form import ParameterDialogForm


class Polynomial2DStorageParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a Polynomial2DStorageParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="coefficients",
                        field_type=Polynomial2DCoefficientsWidget,
                        value=self.form.field_value("coefficients"),
                        help_text="Define the coefficients. You can set, as the "
                        "polynomial independent variables, the volume from a storage "
                        "node and a parameter value",
                    )
                ],
                "First independent variable": [
                    FieldConfig(
                        name="storage_node",
                        label="Storage from node",
                        field_type=StoragePickerWidget,
                        value=self.form.field_value("storage_node"),
                        help_text="Use the storage from the node specified above "
                        "as independent variable for the polynomial",
                    ),
                    FieldConfig(
                        name="use_proportional_volume",
                        field_type="boolean",
                        default_value=False,
                        value=self.form.field_value("use_proportional_volume"),
                        help_text="If Yes the independent variable is the proportional "
                        "volume (between 0 and 1) of the Storage node",
                    ),
                    FieldConfig(
                        name="storage_offset",
                        value=self.form.field_value("storage_offset"),
                        field_type=FloatWidget,
                        default_value=None,
                        help_text="Offset the storage by the provided amount. Default "
                        "to empty to ignore",
                    ),
                    FieldConfig(
                        name="storage_scale",
                        field_type=FloatWidget,
                        default_value=None,
                        value=self.form.field_value("storage_scale"),
                        help_text="Scale the storage by the provided "
                        "amount before applying the offset. Default to empty to ignore",
                    ),
                ],
                "Second independent variable": [
                    FieldConfig(
                        name="parameter",
                        label="Value from parameter",
                        field_type=ParameterLineEditWidget,
                        value=self.form.field_value("parameter"),
                        help_text="Use the value from the parameter specified above "
                        "as independent variable for the polynomial",
                    ),
                    FieldConfig(
                        name="parameter_offset",
                        value=self.form.field_value("parameter_offset"),
                        field_type=FloatWidget,
                        default_value=None,
                        help_text="Offset the parameter value by the provided amount. "
                        "Default to empty to ignore",
                    ),
                    FieldConfig(
                        name="parameter_scale",
                        field_type=FloatWidget,
                        default_value=None,
                        value=self.form.field_value("parameter_scale"),
                        help_text="Scale the parameter value by the provided "
                        "amount before applying the offset. Default to empty to ignore",
                    ),
                ],
                "Miscellaneous": [self.form.comment],
            }
        )

    def filter(self, form_data: dict) -> None:
        """
        Converts the dictionary of coefficients to a list of 2 nested lists.
        :return: None
        """
        value_list = []
        for values in form_data["coefficients"].values():
            value_list.append(values)

        form_data["coefficients"] = value_list
