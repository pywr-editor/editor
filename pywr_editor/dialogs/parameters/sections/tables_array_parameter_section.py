from pywr_editor.form import (
    CheckSumWidget,
    FieldConfig,
    FormSection,
    H5FileWidget,
    H5NodeWidget,
    H5WhereWidget,
    ScenarioPickerWidget,
)

from ..parameter_dialog_form import ParameterDialogForm


class TablesArrayParameterSection(FormSection):
    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict,
    ):
        """
        Initialises the form section for TablesArrayParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="url",
                        label="URL",
                        field_type=H5FileWidget,
                        value=self.form.field_value("url"),
                        help_text="The location of the HDF file",
                    ),
                    FieldConfig(
                        name="where",
                        field_type=H5WhereWidget,
                        value=self.form.field_value("where"),
                        help_text="The path where to read the node in the table",
                    ),
                    FieldConfig(
                        name="node",
                        field_type=H5NodeWidget,
                        value=self.form.field_value("node"),
                        help_text="The node name identifying the table",
                    ),
                    FieldConfig(
                        name="scenario",
                        field_type=ScenarioPickerWidget,
                        field_args={"is_mandatory": False},
                        value=self.form.field_value("scenario"),
                        help_text="Use as many table columns as the size of the "
                        "provided scenario. Each column acts as an ensemble whose "
                        "values must match the number of time steps. If the scenario "
                        "is omitted, only the first table colum will be used",
                    ),
                ],
                "Miscellaneous": [
                    FieldConfig(
                        name="timestep_offset",
                        label="Time offset",
                        field_type="integer",
                        # default to 0 to remove the offset on save
                        default_value=0,
                        value=self.form.field_value("timestep_offset"),
                        help_text="When provided, the parameter will return the table "
                        "value corresponding to the current model time-step plus or "
                        "minus the offset. The offset can be used to look forward "
                        "(when positive) or backward (when negative) in the table. "
                        "If the offset takes the time index out of the data bounds, "
                        "the parameter will return the first or last value available",
                    ),
                    FieldConfig(
                        name="checksum",
                        field_type=CheckSumWidget,
                        value=self.form.field_value("checksum"),
                        help_text="Validate the H5 file using the provided hash "
                        "generated with the selected algorithm",
                    ),
                    self.form.comment,
                ],
            }
        )
