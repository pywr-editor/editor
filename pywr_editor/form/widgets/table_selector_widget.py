import os
import traceback
from typing import TYPE_CHECKING

import pandas as pd
import qtawesome as qta
from pandas import read_csv, read_excel, read_hdf
from PySide6.QtCore import QSize, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QMessageBox, QSizePolicy

from pywr_editor.form import FormCustomWidget, FormField, Validation
from pywr_editor.model import ModelConfig
from pywr_editor.utils import (
    Logging,
    get_index_names,
    get_signal_sender,
    reset_pandas_index_names,
    set_table_index,
)
from pywr_editor.widgets import ComboBox, ExtensionIcon, PushIconButton

if TYPE_CHECKING:
    from pywr_editor.form import ModelComponentForm


"""
 This widget loads and handles slots and signals
 when the table is defined in the model table section.

 All files: the DataFrame index cannot be changed. The
 index_col and parse_dates fields are always hidden.
 Fields visibility is handled by the SourceSelectorWidget.
"""


class TableSelectorWidget(FormCustomWidget):
    updated_table = Signal()
    register_updated_table = ["index", "column"]

    def __init__(
        self,
        name: str,
        value: str,
        parent: FormField,
        available_tables: list[str] | None = None,
        log_name: str = None,
        static: bool = False,
    ):
        """
        Initialises the widget to provide a list of the available model tables. A table
        file can be opened externally by clicking on the "Open" button, or the table
        content can be reloaded using the "Reload" button.
        :param name: The field name.
        :param value: The selected table name.
        :param parent: The parent widget.
        :param available_tables: A list of table names to use. Default to None to use
         all the available tables
        in the model.
        :param log_name: The name to use in the logger.
        :param static: Show only a list of tables. No data is loaded and the action
        buttons are hidden. Default to False.
        """
        if log_name is None:
            log_name = self.__class__.__name__

        self.logger = Logging().logger(log_name)
        self.logger.debug(f"Loading widget with {value}")
        self.static = static

        super().__init__(name, value, parent)
        self.form: "ModelComponentForm"
        self.model_config: ModelConfig = self.form.model_config
        self.supported_extensions = [
            ".csv",
            ".txt",
            ".xls",
            ".xlsx",
            ".xlsm",
            ".h5",
        ]
        self.table_parse_error = False

        # set model tables
        self.tables = self.model_config.tables
        if available_tables is None:
            self.table_names = self.tables.names
        else:
            self.table_names = available_tables
        self.logger.debug(
            f"Using the following table names: {', '.join(self.table_names)}"
        )

        # table data
        self.table = None
        self.file = None
        self.file_ext = None
        self.index_names = []

        # populate ComboBox
        self.combo_box = ComboBox()
        self.combo_box.setIconSize(QSize(21, 16))
        self.combo_box.addItems(["None"])
        for name in self.table_names:
            ext = self.model_config.tables.get_extension(table_name=name)
            if ext is None:
                ext = "N/A"
            self.combo_box.addItem(QIcon(ExtensionIcon(ext)), name)
        # Open button
        self.open_button = PushIconButton(
            icon=qta.icon("msc.table"), label="Open", small=True
        )
        self.open_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.open_button.setToolTip(
            "Open the table file externally with the default associated application"
        )
        # noinspection PyUnresolvedReferences
        self.open_button.clicked.connect(self.on_open_file)

        # Reload button
        self.reload_button = PushIconButton(
            icon=qta.icon("msc.refresh"), label="Reload"
        )
        self.reload_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.reload_button.setToolTip(
            "Reload the column names from the file in case its content changed"
        )
        # noinspection PyUnresolvedReferences
        self.reload_button.clicked.connect(self.on_reload_click)

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)
        if not static:
            layout.addWidget(self.open_button)
            layout.addWidget(self.reload_button)

        # initialise field
        self.form.register_after_render_action(self.after_field_render)

    def after_field_render(self) -> None:
        """
        Populates the widget after the entire form is rendered to access to other
        fields.
        :return: None
        """
        # populate field for the first time
        self.on_populate_field(self.value)

        # reload data when data changes
        # noinspection PyUnresolvedReferences
        self.combo_box.currentTextChanged.connect(self.on_update_value)

        # register updated_table Slot When the table changes, When the table changes,
        # the fields using the table content must be updated
        for field_name in self.register_updated_table:
            form_field = self.form.find_field_by_name(field_name)
            if form_field is None:
                self.logger.debug(
                    f"Skipping registration of Slot {field_name}.update_field because "
                    + "field does not exist"
                )
                continue

            form_widget = form_field.widget
            if not hasattr(form_widget, "update_field"):
                raise NotImplementedError(
                    f"The widget {form_widget} must have the update_field() method"
                )
            # noinspection PyUnresolvedReferences
            self.updated_table.connect(form_widget.update_field)
            self.logger.debug(
                f"Registered Slot {form_widget.name}.update_field for "
                + "updated_table Signal"
            )

    @Slot()
    def on_reload_click(self) -> None:
        """
        Reloads the table stored by the widget when the Reload button is clicked.
        :return: None
        """
        self.logger.debug(f"Called on_reload_click Slot from {get_signal_sender(self)}")
        self.load_table_data(self.value)
        self.logger.debug("Completed on_reload_click Slot")

    @Slot(str)
    def on_populate_field(self, table_name: str) -> None:
        """
        Updates the table. This is called to populate the widget the first time.
        :param table_name: The name of the table.
        :return: None
        """
        self.logger.debug(
            f"Running on_populate_field Slot with file '{table_name}' from "
            + get_signal_sender(self)
        )
        # prevent setCurrentText from triggering update slot
        self.combo_box.blockSignals(True)

        # init
        self.form_field.clear_message()
        self.combo_box.setEnabled(False)
        self.open_button.setEnabled(False)
        self.reload_button.setEnabled(False)
        self.combo_box.setCurrentText("None")

        # read the file and update the table
        self.load_table_data(table_name)

        # table names list is None or an empty list
        if not self.table_names:
            message = "The are no tables defined in the model configuration"
            self.logger.debug(message)
            self.form_field.set_warning_message(message)
        else:
            # enable the ComboBox and set the selection
            self.combo_box.setEnabled(True)

            if table_name is None:
                self.logger.debug("Table name is None")
            # wrong type
            elif table_name is not None and not isinstance(table_name, str):
                message = "The table in the model configuration must be a string"
                self.logger.debug(message)
                self.form_field.set_warning_message(message)
            # valid string
            elif table_name is not None:
                if table_name in self.table_names:
                    self.logger.debug(f"Setting value to '{table_name}'")
                    self.combo_box.setCurrentText(table_name)

                # skip file check if widget is static
                if not self.static:
                    if self.file is None:
                        message = "The table file does not exist"
                        self.logger.debug(message)
                        self.form_field.set_warning_message(message)
                        # let user reload file if it is later created (as long as
                        # table exists)
                        if table_name in self.table_names:
                            self.reload_button.setEnabled(True)
                    elif self.file_ext not in self.supported_extensions:
                        message = (
                            f"The file extension '{self.file_ext}' is not "
                            + "supported"
                        )
                        self.logger.debug(message)
                        self.form_field.set_warning_message(message)
                    elif self.table_parse_error:
                        self.form_field.set_error_message(
                            "Cannot parse the file. The provided table options are "
                            + "wrong. You can change them in the Table dialog"
                        )
                    # file exists and can be opened
                    else:
                        self.logger.debug("Enabling buttons")
                        self.open_button.setEnabled(True)
                        self.reload_button.setEnabled(True)

                    if table_name not in self.table_names:
                        message = (
                            f"The table name '{table_name}', set in the model "
                            + "configuration, does not exist"
                        )
                        self.form_field.set_warning_message(message)
                        self.logger.debug(message)

        self.combo_box.blockSignals(False)
        self.logger.debug("Completed on_populate_field Slot")

    @Slot(str)
    def on_update_value(self, selected_name: str) -> None:
        """
        Slot triggered when the table name changes in the field selector. This stores
        the new name internally and loads the table.
        :param selected_name: The selected item in the QComboBox.
        :return: None
        """
        self.logger.debug(
            f"Running on_update_value Slot with value {selected_name} from "
            + get_signal_sender(self)
        )

        if selected_name == "None":
            self.value = None
        else:
            self.value = selected_name
        self.logger.debug(f"Updated field value to '{self.value}'")

        # reload table data and set form messages
        self.on_populate_field(self.value)
        self.logger.debug("Completed on_update_value Slot")

    def load_table_data(self, table_name: str) -> None:
        """
        Loads the table.
        :param table_name: The name of the table.
        :return: None.
        """
        self.logger.debug("Running load_data_table()")
        if self.static:
            self.logger.debug("Skipped because widget is static")
            return None

        self.table = None
        self.table_parse_error = False
        self.file = None
        self.file_ext = None
        self.index_names = None

        # load the table data
        table_dict = self.tables.config(table_name)
        self.logger.debug(f"Table dictionary for '{table_name}' is: {table_dict}")
        if table_dict is not None:
            self.index_names = table_dict.get("index_col")

            # read the file
            self.file = table_dict.get("url")
            if self.file is None:
                self.logger.debug("The file is not valid")
            elif self.model_config.does_file_exist(self.file) is False:
                self.logger.debug(f"The file {self.file} does not exist")
                self.file = None
            else:
                self.file = self.model_config.normalize_file_path(self.file)
                _, self.file_ext = os.path.splitext(self.file)

                # try parsing the file
                # noinspection PyBroadException
                try:
                    if self.file_ext == ".csv" or self.file_ext == ".txt":
                        args = {}
                        for name in [
                            "sep",
                            "skipinitialspace",
                            "skipfooter",
                            "skip_blank_lines",
                        ]:
                            if name in table_dict:
                                args[name] = table_dict[name]
                        args["low_memory"] = True
                        self.logger.debug(f"Opening CSV file {self.file} using: {args}")
                        self.table = read_csv(self.file, **args)
                    elif self.file_ext in [".xls", ".xlsx", ".xlsm"]:
                        args = {}
                        for name in [
                            "sheet_name",
                        ]:
                            if name in table_dict:
                                args[name] = table_dict[name]
                        self.logger.debug(
                            f"Opening Excel file {self.file} using: {args}"
                        )
                        self.table = read_excel(self.file, **args)
                    elif self.file_ext == ".h5":
                        args = {}
                        for name in [
                            "start",
                            "key",
                        ]:
                            if name in table_dict:
                                args[name] = table_dict[name]
                        self.logger.debug(f"Opening H5 file {self.file} using: {args}")
                        # noinspection PyTypeChecker
                        self.table: pd.DataFrame = read_hdf(self.file, **args)
                        # remove built-in indexes and set them via attrs
                        # for H5 file, index names cannot be changed
                        index_names = reset_pandas_index_names(self.table)
                        self.logger.debug(f"Resetting built-in indexes: {index_names}")
                        set_table_index(self.table, index_names)

                    if (
                        self.file_ext not in self.supported_extensions
                        and self.table is None
                    ):
                        self.logger.debug("Failed to open the table file")
                        raise ValueError("Extension not supported")
                except Exception:
                    self.logger.debug(
                        "Cannot parse the file due to Exception: "
                        + f"{traceback.print_exc()}"
                    )
                    self.table_parse_error = True
        else:
            self.logger.debug("No table data available to parse the file")

        self.logger.debug(f"DataFrame is\n {self.table}")

        # set index for non-H5 files
        if self.table is not None and not self.table.empty and self.file_ext != ".h5":
            self.logger.debug(f"Preparing to set index ({self.index_names}) on table")
            if self.index_names is not None:
                set_table_index(self.table, self.index_names)
                self.logger.debug(
                    f"Stored new indexes in table '{get_index_names(self.table)}'"
                )
            else:
                self.logger.debug("Index not provided")

        self.logger.debug("Emitting updated_table Signal")
        # noinspection PyUnresolvedReferences
        self.updated_table.emit()

    @Slot()
    def on_open_file(self) -> None:
        """
        Opens the table file externally.
        :return: None
        """
        # noinspection PyBroadException
        try:
            table_name = self.value
            table_config = self.tables.config(table_name)
            # convert to absolute path
            file = self.model_config.normalize_file_path(table_config["url"])
            # ensure that the path is properly encoded
            file = os.path.normpath(file)
            os.startfile(file)
        except Exception:
            self.logger.debug(f"Cannot open the file because: {traceback.print_exc()}")
            QMessageBox().critical(
                self,
                "Cannot open the file",
                "An error occurred while trying to open the file",
            )

    def get_value(self) -> str | None:
        """
        Returns the form field value.
        :return: The form field value.
        """
        value = self.combo_box.currentText()
        if value == "None":
            return None
        return value

    def validate(
        self,
        name: str,
        label: str,
        value: str | None,
    ) -> Validation:
        """
        Checks that a valid table is provided.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value from self.get_value().
        :return: The Validation instance.
        """
        self.logger.debug("Validating field")

        if value is None or value not in self.table_names:
            self.logger.debug("Validation failed")
            return Validation("You must select a valid table from the list")
        elif not self.static and self.table is None:
            self.logger.debug("Validation failed")
            return Validation(
                "The table file is not valid. Please select another "
                "table or make sure the file exists",
            )
        self.logger.debug("Validation passed")
        return Validation()

    def reset(self) -> None:
        """
        Resets the widget. This sets the value of the ComboBox to None and emits the
        updated_table Slot to force all the dependant fields to reset. The
        self.combo_box.currentTextChanged Signal does emit the updated_table Signal,
        but only if the ComboBox selection is not "None" when it is reset.
        :return: None
        """
        # block signal to avoid triggering updated_table twice if field is not
        # already "None"
        self.blockSignals(True)
        self.combo_box.setCurrentText("None")
        self.blockSignals(False)

        # noinspection PyUnresolvedReferences
        self.updated_table.emit()
