from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import QPushButton

from pywr_editor.form import (
    BooleanWidget,
    FieldConfig,
    Form,
    H5KeyWidget,
    IndexColWidget,
    IntegerWidget,
    ParseDatesWidget,
    SheetNameWidget,
    Validation,
)
from pywr_editor.model import ModelConfig

from .table_url_widget import TableUrlWidget

if TYPE_CHECKING:
    from .table_page import TablePage


class TableFormWidget(Form):
    def __init__(
        self,
        name: str,
        model_config: ModelConfig,
        table_dict: dict,
        save_button: QPushButton,
        page: "TablePage",
    ):
        """
        Initialises the table form.
        :param name: The table name.
        :param model_config: The ModelConfig instance.
        :param save_button: The button used to save the form.
        :param table_dict: The table configuration.
        :param page: The parent widget.
        """
        self.name = name
        self.model_config = model_config
        self.table_dict = table_dict
        self.page = page

        available_fields = {
            "Basic information": [
                FieldConfig(
                    name="name",
                    value=name,
                    help_text="A unique name identifying the table",
                    allow_empty=False,
                    validate_fun=self._check_table_name,
                ),
                FieldConfig(
                    name="url",
                    label="URL",
                    field_type=TableUrlWidget,
                    value=self.field_value("url"),
                    allow_empty=False,
                    help_text="The location of the file to use for the table (CSV, "
                    "XLS, XLSX or H5). When possible, the path is automatically set "
                    "relative to the model configuration file",
                ),
                FieldConfig(
                    name="sheet_name",
                    field_type=SheetNameWidget,
                    value=self.field_value("sheet_name"),
                    default_value=0,
                    help_text="The name of the Excel sheet where to get the table",
                ),
                FieldConfig(
                    name="key",
                    field_type=H5KeyWidget,
                    value=self.field_value("key"),
                    help_text="The name of the key that identifies the table",
                ),
            ],
            "Parsing options": [
                FieldConfig(
                    name="sep",
                    label="Separator",
                    value=self.field_value("sep"),
                    default_value=",",
                    help_text="The delimiter used to separate the columns in the "
                    "CSV file. Default to ','",
                ),
                FieldConfig(
                    name="dayfirst",
                    field_type=BooleanWidget,
                    default_value=False,
                    value=self.field_value("dayfirst"),
                    help_text="Use international and European format for dates "
                    "(DD/MM). Default to No",
                ),
                FieldConfig(
                    name="skipinitialspace",
                    label="Skip initial space",
                    value=self.field_value("skipinitialspace"),
                    default_value=False,
                    field_type=BooleanWidget,
                    help_text="Skip any space after the separator, if any. "
                    'For example "   Date" is converted to "Date"',
                ),
                FieldConfig(
                    name="skipfooter",
                    label="Skip footer",
                    value=self.field_value("skipfooter"),
                    default_value=0,
                    field_type=IntegerWidget,
                    field_args={"min_value": 0},
                    help_text="Number of lines at bottom of file to skip. Default to 0",
                ),
                FieldConfig(
                    name="skip_blank_lines",
                    value=self.field_value("skip_blank_lines"),
                    default_value=True,
                    field_type=BooleanWidget,
                    help_text="If Yes, skip over blank lines rather than "
                    "interpreting as NaN values. Default to Yes",
                ),
                FieldConfig(
                    name="start",
                    label="Starting row",
                    value=self.field_value("start"),
                    default_value=0,
                    field_type=IntegerWidget,
                    field_args={"min_value": 0},
                    help_text="Line numbers to skip at the start of the table",
                ),
            ],
            "Table configuration": [
                FieldConfig(
                    name="index_col",
                    field_type=IndexColWidget,
                    value=self.field_value("index_col"),
                    help_text="The column name to use as the row labels of the "
                    "table",
                ),
                FieldConfig(
                    name="parse_dates",
                    field_type=ParseDatesWidget,
                    value={
                        "parse_dates": self.field_value("parse_dates"),
                        "index_col": self.field_value("index_col"),
                    },
                    help_text="The column name that contains the dates to parse",
                ),
            ],
        }

        super().__init__(
            fields=available_fields,
            save_button=save_button,
            parent=page,
            direction="vertical",
        )

    def field_value(self, key: str) -> Any:
        """
        Gets a value from the table configuration.
        :param key: The key to extract the value of.
        :return: The value or empty if the key is not set.
        """
        return super().get_dict_value(key, self.table_dict)

    def _check_table_name(self, name: str, label: str, value: str) -> Validation:
        """
        Checks that the new table name is not duplicated.
        :param name: The field name.
        :param label: The field label.
        :param value: The table name.
        :return: True if the name validates correctly, False otherwise.
        """
        # do not save form if the table name is changed and already exists
        if self.name != value and self.model_config.tables.exists(value) is True:
            return Validation(
                f'The table "{value}" already exists. Please provide a different name'
            )
        return Validation()
