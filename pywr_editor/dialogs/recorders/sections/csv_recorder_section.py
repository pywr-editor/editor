from pywr_editor.form import (
    CSVCompressionLibWidget,
    CSVDialectWidget,
    FieldConfig,
    FileBrowserWidget,
    FormSection,
    IntegerWidget,
    MultiNodePickerWidget,
    Validation,
)

from ..recorder_dialog_form import RecorderDialogForm


class CSVRecorderSection(FormSection):
    def __init__(self, form: RecorderDialogForm, section_data: dict):
        """
        Initialises the form section for CSVRecorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="url",
                        label="File",
                        field_type=FileBrowserWidget,
                        field_args={"file_extension": "csv"},
                        value=form.field_value("url"),
                        help_text="The path where the recorder saves the CSV file",
                    ),
                    FieldConfig(
                        name="nodes",
                        value=form.field_value("nodes"),
                        field_type=MultiNodePickerWidget,
                        help_text="A list of nodes to export. The recorder exports "
                        "all nodes, when no node is selected",
                    ),
                    FieldConfig(
                        name="scenario_index",
                        label="Scenario/combination index",
                        value=form.field_value("scenario_index"),
                        field_type=IntegerWidget,
                        field_args={"min_value": 0},
                        default_value=0,
                        help_text="A number starting from 0 indicating the index of "
                        "scenario or combination to export. Set it to 0, when no "
                        "scenario is configured",
                    ),
                    form.comment,
                ],
                "Advanced": [
                    FieldConfig(
                        name="complib",
                        label="Compression algorithm",
                        field_type=CSVCompressionLibWidget,
                        value=form.field_value("complib"),
                    ),
                    FieldConfig(
                        name="complevel",
                        label="Compression level",
                        field_type=IntegerWidget,
                        field_args={"min_value": 0, "max_value": 9},
                        default_value=9,
                        validate_fun=self.check_complevel,
                        value=form.field_value("complevel"),
                    ),
                    FieldConfig(
                        name="dialect",
                        label="CSV dialect",
                        field_type=CSVDialectWidget,
                        value=form.field_value("dialect"),
                    ),
                ],
            }
        )

    def check_complevel(self, name: str, label: str, value: int) -> Validation:
        """
        Checks the compression level.
        :param name: The field name.
        :param label: The field value.
        :param value: The field value.
        :return: The validation instance.
        """
        complib_value = self.form.find_field("complib").value()
        if complib_value and complib_value == "bzip2" and value == 0:
            return Validation(
                "The minimum compression level for the BZIP2 algorithm is 1"
            )
        return Validation()
