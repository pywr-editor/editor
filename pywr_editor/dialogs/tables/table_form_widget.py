from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import QPushButton

from pywr_editor.form import (
    FieldConfig,
    Form,
    H5KeyWidget,
    IndexColWidget,
    ParseDatesWidget,
    SheetNameWidget,
    Validation,
)
from pywr_editor.model import ModelConfig

from .table_url_widget import TableUrlWidget

if TYPE_CHECKING:
    from .table_page_widget import TablePageWidget


class TableFormWidget(Form):
    def __init__(
        self,
        name: str,
        model_config: ModelConfig,
        table_dict: dict,
        save_button: QPushButton,
        parent: "TablePageWidget",
    ):
        """
        Initialises the table form.
        :param name: The table name.
        :param model_config: The ModelConfig instance.
        :param save_button: The button used to save the form.
        :param table_dict: The table configuration.
        :param parent: The parent widget.
        """
        self.name = name
        self.model_config = model_config
        self.table_dict = table_dict
        self.page = parent

        self.defaults = {  # TODO
            # this should be None; to simplify widget use empty list which behaves like
            # None in pandas. This will not be included in final JSON when index_col==[]
            "index_col": [],
            "parse_dates": [],
            "dayfirst": False,
            "skipinitialspace": False,
            "skipfooter": 0,
            "skip_blank_lines": True,
            "sheet_name": 0,
            "key": None,
            "start": 0,
        }

        available_fields: dict[str, list[FieldConfig]] = {
            "Basic information": [
                {
                    "name": "name",
                    "value": name,
                    "help_text": "A unique name identifying the table",
                    "allow_empty": False,
                    "validate_fun": self._check_table_name,
                },
                {
                    "name": "url",
                    "label": "URL",
                    "field_type": TableUrlWidget,
                    "value": self.get_table_dict_value("url"),
                    "allow_empty": False,
                    "help_text": "The location of the file to use for the table (CSV, "
                    + "XLS, XLSX or H5). When possible, the path is automatically set "
                    + "relative to the model configuration file",
                },
                {
                    "name": "sheet_name",
                    "field_type": SheetNameWidget,
                    "value": self.get_table_dict_value("sheet_name"),
                    "help_text": "The name of the Excel sheet where to get the table",
                },
                {
                    "name": "key",
                    "field_type": H5KeyWidget,
                    "value": self.get_table_dict_value("key"),
                    "help_text": "The name of the key that identifies the table",
                },
            ],
            "Parsing options": [
                {
                    "name": "sep",
                    "label": "Separator",
                    "value": self.get_table_dict_value("sep"),
                    "default_value": ",",
                    "help_text": "The delimiter used to separate the columns in the "
                    + "CSV file. Default to ','",
                },
                {
                    "name": "dayfirst",
                    "field_type": "boolean",
                    "value": self.get_table_dict_value("dayfirst"),
                    "help_text": "Use international and European format for dates "
                    + "(DD/MM). Default to No",
                },
                {
                    "name": "skipinitialspace",
                    "label": "Skip initial space",
                    "value": self.get_table_dict_value("skipinitialspace"),
                    "field_type": "boolean",
                    "help_text": "Skip any space after the separator, if any. "
                    + 'For example "   Date" is converted to "Date"',
                },
                {
                    "name": "skipfooter",
                    "label": "Skip footer",
                    "value": self.get_table_dict_value("skipfooter"),
                    "field_type": "integer",
                    "min_value": 0,
                    "help_text": "Number of lines at bottom of file to skip. Default "
                    + "to 0",
                },
                {
                    "name": "skip_blank_lines",
                    "value": self.get_table_dict_value("skip_blank_lines"),
                    "field_type": "boolean",
                    "help_text": "If Yes, skip over blank lines rather than "
                    + "interpreting as NaN values. Default to Yes",
                },
                {
                    "name": "start",
                    "label": "Starting row",
                    "value": self.get_table_dict_value("start"),
                    "default_value": 0,
                    "field_type": "integer",
                    "min_value": 0,
                    "help_text": "Line numbers to skip at the start of the table",
                },
            ],
            "Table configuration": [
                {
                    "name": "index_col",
                    "field_type": IndexColWidget,
                    "value": self.get_table_dict_value("index_col"),
                    "help_text": "The column name to use as the row labels of the "
                    + "table",
                },
                {
                    "name": "parse_dates",
                    "field_type": ParseDatesWidget,
                    "value": {
                        "parse_dates": self.get_table_dict_value("parse_dates"),
                        "index_col": self.get_table_dict_value("index_col"),
                    },
                    "help_text": "The column name that contains the dates to parse",
                },
            ],
        }

        super().__init__(
            available_fields,
            self.defaults,
            save_button,
            parent,
            direction="vertical",
        )

    def get_table_dict_value(self, key: str) -> Any:
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
                f'The table "{value}" already exists. '
                "Please provide a different name."
            )
        return Validation()
