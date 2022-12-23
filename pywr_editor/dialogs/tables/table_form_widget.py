from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMessageBox, QPushButton

from pywr_editor.form import (
    FieldConfig,
    Form,
    FormValidation,
    H5KeyWidget,
    IndexColWidget,
    ParseDatesWidget,
    SheetNameWidget,
)
from pywr_editor.model import JsonUtils, ModelConfig
from pywr_editor.utils import get_columns

from .table_url_widget import TableUrlWidget
from .tables_list_model import TablesListModel

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

    def _check_table_name(
        self, name: str, label: str, value: str
    ) -> FormValidation:
        """
        Checks that the new table name is not duplicated.
        :param name: The field name.
        :param label: The field label.
        :param value: The table name.
        :return: True if the name validates correctly, False otherwise.
        """
        # do not save form if the table name is changed and already exists
        if (
            self.name != value
            and self.model_config.tables.does_table_exist(value) is True
        ):
            return FormValidation(
                validation=False,
                error_message=f'The table "{value}" already exists. '
                + "Please provide a different name.",
            )
        return FormValidation(validation=True)

    def maybe_new_index(self) -> bool:
        """
        Asks user if they want to change the table index.
        :return: True whether to continue, False otherwise.
        """
        dict_utils = JsonUtils(self.model_config.json)
        output = dict_utils.find_str(self.name, match_key="table")

        if output.occurrences == 0:
            return True

        comp_list = [f"   - {p.replace('/table', '')}" for p in output.paths]
        # truncate list if it's too long
        if len(comp_list) > 10:
            comp_list = comp_list[0:10] + [
                f"\n and {len(comp_list)-10} more components"
            ]

        answer = QMessageBox.warning(
            self,
            "Warning",
            "You are going to change the index names of the table. This may break the "
            + "configuration of the following model components, if they rely on the "
            + "table index to fetch their values: \n\n"
            + "\n".join(comp_list)
            + "\n\n"
            "Do you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            return True
        # on discard or No
        return False

    @Slot()
    def on_save(self) -> None:
        """
        Slot called when user clicks on the "Update" button. Only visible fields are
         exported.
        :return: None
        """
        form_data = self.validate()
        if form_data is False:
            return

        # delete empty fields (None or empty list - for example parse_dates is
        # optional)
        keys_to_delete = []
        [
            keys_to_delete.append(key)
            for key, value in form_data.items()
            if not value
        ]
        [form_data.pop(key, None) for key in keys_to_delete]

        # check changes to index
        prev_index = self.get_table_dict_value("index_col")
        new_index = (
            form_data["index_col"] if "index_col" in form_data.keys() else None
        )
        url_widget: TableUrlWidget = self.find_field_by_name("url").widget
        if (
            prev_index
            and new_index
            and url_widget.table is not None
            and url_widget.file_ext != ".h5"
        ):
            # if index was numeric, check that it has not changed when converted to str
            if isinstance(prev_index[0], int):
                # noinspection PyBroadException
                try:
                    column_names = get_columns(
                        url_widget.table, include_index=True
                    )
                    prev_index = [column_names[idx] for idx in prev_index]
                except Exception:
                    pass
            # convert to same type
            if isinstance(prev_index, list) and len(prev_index) == 1:
                prev_index = prev_index[0]
            if isinstance(new_index, list) and len(new_index) == 1:
                new_index = new_index[0]

            # abort if the user select No
            if new_index != prev_index:
                if self.maybe_new_index() is False:
                    self.save_button.setEnabled(True)
                    return

        # check if table name has changed
        new_name = form_data["name"]
        if form_data["name"] != self.name:
            # update the model configuration
            self.model_config.tables.rename(self.name, new_name)

            # update the page name in the list
            # noinspection PyUnresolvedReferences
            self.page.pages.rename_page(self.name, new_name)

            # update the page title
            self.page.set_page_title(new_name)

            # update the table list
            # noinspection PyUnresolvedReferences
            table_model: TablesListModel = (
                self.page.pages.dialog.table_list_widget.model
            )
            idx = table_model.table_names.index(self.name)
            # noinspection PyUnresolvedReferences
            table_model.layoutAboutToBeChanged.emit()
            table_model.table_names[idx] = new_name
            # noinspection PyUnresolvedReferences
            table_model.layoutChanged.emit()

            self.name = new_name

        # update the model with the new dictionary
        del form_data["name"]
        self.model_config.tables.update(self.name, form_data)

        # update tree and status bar
        app = self.page.pages.dialog.app
        if app is not None:
            if hasattr(app, "components_tree"):
                app.components_tree.reload()
            if hasattr(app, "statusBar"):
                app.statusBar().showMessage(f'Table "{self.name}" updated')
