from typing import Any

from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.form import (
    BooleanWidget,
    ColumnWidget,
    FieldConfig,
    Form,
    H5KeyWidget,
    IndexColWidget,
    IndexWidget,
    IntegerWidget,
    ParseDatesWidget,
    SheetNameWidget,
    SourceSelectorWidget,
    TableSelectorWidget,
    TextWidget,
    UrlWidget,
)
from pywr_editor.model import ModelConfig
from pywr_editor.utils import Logging

"""
 This widgets define an abstract class of a
 form to handle model components such as
 parameters or recorders. The form handles:

  - form data
  - fields to parse external files (CSV, Excel or H5 files)
  - fields to select a model table

 This class does not render any field.
"""


class ModelComponentForm(Form):
    table_config_group_name = "Table configuration"
    optimisation_config_group_name = "Optimisation"

    def __init__(
        self,
        form_dict: dict,
        model_config: ModelConfig,
        fields: dict,
        save_button: QPushButton,
        parent: QWidget,
    ):
        """
        Initialises the form.
        :param form_dict: A dictionary containing the form data.
        :param fields: A dictionary containing the form fields.
        :param model_config: The ModelConfig instance.
        :param save_button: The button used to save the form.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)

        self.model_config = model_config
        self.form_dict = form_dict
        self.logger.debug(f"Loading with {self.form_dict}")

        # clean up dictionary if it contains mixed configurations
        # (for example for table and external file)
        self.section_form_data = {
            "model_config": model_config,
        }

        super().__init__(
            fields=fields,
            save_button=save_button,
            parent=parent,
            direction="vertical",
        )

    def field_value(self, key: str) -> Any:
        """
        Gets a value from the dictionary containing the form data.
        :param key: The key to extract the value of.
        :return: The value or empty if the key is not set.
        """
        return super().get_dict_value(key, self.form_dict)

    def save(self) -> dict | bool:
        """
        Validates the form and return the form dictionary.
        :return: The form dictionary or False if the validation fails.
        """
        self.logger.debug("Saving form")

        form_data = self.validate()
        if form_data is False:
            self.logger.debug("Validation failed")
            return False

        return form_data

    @property
    def source_field(self) -> dict:
        """
        Returns the form configuration for the "source" field.
        :return: The field dictionary.
        """
        return FieldConfig(
            name="source",
            label="Source type",
            field_type=SourceSelectorWidget,
            help_text="Specify where to get the value from",
            value=self.form_dict,
        )

    @property
    def source_field_wo_value(self) -> dict:
        """
        Returns the form configuration for the "source" field.
        :return: The field dictionary.
        """
        return FieldConfig(
            name="source",
            label="Source type",
            field_type=SourceSelectorWidget,
            field_args={"enable_value_source": False},
            help_text="Specify where to get the value from",
            value=self.form_dict,
        )

    @property
    def table_field(self) -> dict:
        """
        Returns the form configuration for the "table" field.
        :return: The field dictionary.
        """
        return FieldConfig(
            name="table",
            field_type=TableSelectorWidget,
            value=self.field_value("table"),
            help_text="Use the value(s) from the selected table",
        )

    @property
    def url_field(self) -> dict:
        """
        Returns the form configuration for the "url" field.
        :return: The field dictionary.
        """
        return FieldConfig(
            name="url",
            label="URL",
            field_type=UrlWidget,
            value=self.field_value("url"),
            allow_empty=False,
            help_text="The location of the file to use for the table (CSV, "
            "TXT, XLS, XLSX, XLSM or H5). When possible, the path is automatically "
            "set relative to the model configuration file",
        )

    @property
    def csv_parse_fields(self) -> list[FieldConfig]:
        """
        Returns a list with the form configurations for the fields used to parse CSV
        files.
        :return: The field dictionary.
        """
        return [
            FieldConfig(
                name="sep",
                label="Separator",
                default_value=",",
                value=self.field_value("sep"),
                help_text="The delimiter used to separate the columns in the CSV "
                "file. Default to ','",
            ),
            FieldConfig(
                name="dayfirst",
                field_type=BooleanWidget,
                default_value=False,
                value=self.field_value("dayfirst"),
                help_text="Use international and European format for dates (DD/MM)."
                " Default to No",
            ),
            FieldConfig(
                name="skipinitialspace",
                label="Skip initial space",
                value=self.field_value("skipinitialspace"),
                default_value=False,
                field_type=BooleanWidget,
                help_text="Skip any space after the separator, if any. For "
                'example "   Date" is converted to "Date"',
            ),
            FieldConfig(
                name="skipfooter",
                label="Skip footer",
                value=self.field_value("skipfooter"),
                field_type=IntegerWidget,
                field_args={"min_value": 0},
                default_value=0,
                help_text="Number of lines at bottom of file to skip. Default to 0",
            ),
            FieldConfig(
                name="skip_blank_lines",
                value=self.field_value("skip_blank_lines"),
                field_type=BooleanWidget,
                default_value=True,
                help_text="If Yes, skip over blank lines rather than interpreting "
                "as NaN values. Default to Yes",
            ),
        ]

    @property
    def excel_parse_fields(self) -> list[dict]:
        """
        Returns a list with the form configurations for the fields used to parse
        Excel files.
        :return: The field dictionary.
        """
        return [
            FieldConfig(
                name="sheet_name",
                field_type=SheetNameWidget,
                value=self.field_value("sheet_name"),
                help_text="The name of the Excel sheet where to get the table",
            ),
        ]

    @property
    def h5_parse_fields(self) -> list[dict]:
        """
        Returns a list with the form configurations for the fields used to parse
        H5 files.
        :return: The field dictionary.
        """
        return [
            FieldConfig(
                name="key",
                field_type=H5KeyWidget,
                value=self.field_value("key"),
                help_text="The name of the key that identifies the table",
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
        ]

    @property
    def index_col_field(self) -> dict:
        """
        Returns the form configuration for the "index_col" field.
        :return: The field dictionary.
        """
        return FieldConfig(
            name="index_col",
            field_type=IndexColWidget,
            value=self.field_value("index_col"),
            help_text="The column name to use as the row labels of the table",
        )

    @property
    def parse_dates_field(self) -> dict:
        """
        Returns the form configuration for the "index_col" field.
        :return: The field dictionary.
        """
        return FieldConfig(
            name="parse_dates",
            field_type=ParseDatesWidget,
            value={
                "parse_dates": self.field_value("parse_dates"),
                "index_col": self.field_value("index_col"),
            },
            help_text="The column name that contains the dates to parse",
        )

    @property
    def column_field(self) -> dict:
        """
        Returns the form configuration for the "column" field.
        :return: The field dictionary.
        """
        return FieldConfig(
            name="column",
            field_type=ColumnWidget,
            value=self.field_value("column"),
            help_text="The table column to use for the value(s)",
        )

    @property
    def index_field(self) -> dict:
        """
        Returns the form configuration for the "index" field.
        :return: The field dictionary.
        """
        return FieldConfig(
            name="index",
            label="Row name",
            field_type=IndexWidget,
            value={
                "index": self.field_value("index"),
                "indexes": self.field_value("indexes"),
                "index_col": self.field_value("index_col"),
            },
            help_text="The table row name in the selected column to use for the "
            "value(s)",
        )

    @property
    def comment(self) -> dict:
        """
        Returns the form configuration for the "comment" field.
        :return: The field dictionary.
        """
        return FieldConfig(
            name="comment",
            field_type=TextWidget,
            field_args={"multi_line": True},
            value=self.field_value("comment"),
        )
