import os
import traceback

import qtawesome as qta
from pandas import read_csv, read_excel, read_hdf
from PySide6.QtCore import Signal, SignalInstance, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
)

from pywr_editor.form import FormCustomWidget, FormField, Validation
from pywr_editor.utils import (
    Logging,
    get_signal_sender,
    reset_pandas_index_names,
    set_table_index,
)
from pywr_editor.widgets import PushIconButton

"""
 This widget loads and handles slots and signals for an external
 file or table.

 The widget ignores non-existing fields. For example, ConstantParameter
 makes use of the "index" field to define its value, but all other
 parameters do not.

 H5 files: the DataFrame index cannot be changed. The index_col field
 is shown but it is kept disabled to ensure consistency with other
 table formats. The parse_dates field is not available as data types
 (such as dates) are already defined in the DataFrame object.

 Fields visibility is handled by the SourceSelectorWidget and by this
 widget for the index_col and parse_dates fields (H5 files do not have
 parse_dates but only index_col field).
"""


class UrlWidget(FormCustomWidget):
    # Initialise Signals - signal must be defined on the class, not the instance
    updated_table = Signal()
    index_changed = Signal()
    file_changed: None | SignalInstance = None

    # Fields to parse and change visibility of
    csv_fields: list[str] = [
        "sep",
        "dayfirst",
        "skipinitialspace",
        "skipfooter",
        "skip_blank_lines",
    ]
    excel_fields: list[str] = ["sheet_name"]
    # NOTE: parse_dates not available as data type is already defined in the DataFrame.
    hdf_fields: list[str] = ["key", "start"]
    # Common fields
    common_field: list[str] = ["index_col", "parse_dates"]

    # Signals
    # When the value of the following fields changes, the table gets updated
    force_table_update: list[str] = [
        "sep",
        "dayfirst",
        "skipinitialspace",
        "skipfooter",
        "skip_blank_lines",
        "sheet_name",
        "key",
        "start",
    ]
    # register updated_table Slot for the following fields. When the table changes,
    # the fields gets updated
    register_updated_table: list[str] = [
        "index_col",
        "parse_dates",
        "index",
        "column",
    ]
    # register_updated_table = ["index_col", "parse_dates"]
    # when the file name changes, reload the following widgets
    force_widget_update: list[str] = ["sheet_name", "key"]
    # when index_col changes, index and column fields need updating. This is not
    # triggered when the table is updated, but only when selected indexes
    # actually change
    register_index_changed: list[str] = ["index", "column"]

    def __init__(
        self,
        name: str,
        value: str,
        parent: FormField,
        log_name: str = None,
    ):
        """
        Initialises the input field to edit the table URL.
        :param name: The field name.
        :param value: The table file.
        :param parent: The parent widget.
        :param log_name: The name to use in the logger.
        """
        if log_name is None:
            log_name = self.__class__.__name__

        self.logger = Logging().logger(log_name)
        self.logger.debug(f"Loading widget with {value}")

        super().__init__(name, value, parent)
        self.model_config = self.form.model_config

        # table data
        self.table = None
        self.table_parse_error = False

        # store the new value
        self.full_file = None
        self.file_ext = None
        self.supported_extensions = [
            ".csv",
            ".txt",
            ".xls",
            ".xlsx",
            ".xlsm",
            ".h5",
        ]
        self.on_update_file(value)

        # field
        self.line_edit = QLineEdit()
        self.line_edit.setText(value)
        self.line_edit.setObjectName(f"{name}_line_edit")
        # noinspection PyTypeChecker
        self.file_changed = self.line_edit.textChanged

        # browse button
        self.browse_button = PushIconButton(
            icon=qta.icon("msc.folder-opened"), label="Browse...", small=True
        )

        # open file
        self.open_button = PushIconButton(
            icon=qta.icon("msc.table"), label="Open", small=True
        )
        self.open_button.setToolTip(
            "Open the file externally with the associated application"
        )

        # reload button
        self.reload_button = PushIconButton(
            icon=qta.icon("msc.refresh"), label="Reload", small=True
        )
        self.reload_button.setToolTip(
            "Reload the table file in case its content changed"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.open_button)
        layout.addWidget(self.reload_button)

        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")

        # populate the field for the first time after sheet_name and key widgets have
        # been loaded. These are needed to determine the table to load
        self.on_reload_all_data(self.full_file)

        # 1. connect Slots to field
        # always update file first
        # noinspection PyUnresolvedReferences
        self.file_changed.connect(self.on_update_file)
        # noinspection PyUnresolvedReferences
        self.open_button.clicked.connect(self.on_open_file)
        # noinspection PyUnresolvedReferences
        self.reload_button.clicked.connect(self.on_reload_click)
        # noinspection PyUnresolvedReferences
        self.browse_button.clicked.connect(self.on_browse_table_file)

        # 2. reload the table if the value in the widgets listed in
        # self.force_table_update changes (for ex. separator)
        for field in self.force_table_update:
            form_field = self.form.fields[field]
            if isinstance(form_field.widget, QLineEdit):
                # noinspection PyUnresolvedReferences
                form_field.widget.textChanged.connect(self.on_table_reload)
                self.logger.debug(
                    "Registered Slot on_table_reload for QLineEdit("
                    + f"{form_field.name}).textChanged Signal"
                )
            elif isinstance(form_field.widget, QComboBox):
                # noinspection PyUnresolvedReferences
                form_field.widget.currentIndexChanged.connect(self.on_table_reload)
                self.logger.debug(
                    "Registered Slot on_table_reload for QComboBox("
                    + f"{form_field.name}).currentIndexChanged Signal"
                )
            elif isinstance(form_field.widget, QSpinBox):
                # noinspection PyUnresolvedReferences
                form_field.widget.textChanged.connect(self.on_table_reload)
                self.logger.debug(
                    f"Registered Slot on_table_reload for QSpinBox({form_field.name})."
                    + "textChanged Signal"
                )
            elif form_field.is_custom_widget:
                if not hasattr(form_field.widget, "field_value_changed"):
                    raise NotImplementedError(
                        f"The widget {form_field} must have the field_value_changed "
                        + "attribute"
                    )
                # noinspection PyUnresolvedReferences
                form_field.widget.field_value_changed.connect(self.on_table_reload)
                self.logger.debug(
                    "Registered Slot on_table_reload for custom widget "
                    + f"named {form_field.name}"
                )

        # 3. reload the following widgets if the file name changes (for ex. sheet names)
        for field in self.force_widget_update:
            form_field = self.form.fields[field].widget
            if not hasattr(form_field, "on_update_field"):
                raise NotImplementedError(
                    f"The widget {form_field} must have the update_field() method"
                )
            # noinspection PyUnresolvedReferences
            self.file_changed.connect(form_field.on_update_field)
            self.logger.debug(
                f"Registered Slot {form_field.name}.on_update_field for "
                + "file_changed Signal"
            )

        # 4. register updated_table Slot. When the table changes, the fields using the
        # table content must be updated the fields must have the update method
        for field_name in self.register_updated_table:
            form_field = self.form.find_field(field_name)
            if form_field is None:
                self.logger.debug(
                    f"Skipping registration of Slot {field_name}.update_field for "
                    + "updated_table Signal because field does not exist"
                )
                continue

            # noinspection PyTypeChecker
            form_widget: FormCustomWidget = form_field.widget
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

        # 5. on file change, update all other fields first and then update the table
        self.logger.debug("Registered Slot on_reload_all_data for file_changed Signal")
        # noinspection PyUnresolvedReferences
        self.file_changed.connect(self.on_reload_all_data)

        # 6. when index_col changes, the table indexes must be updated (for index and
        # column widgets)
        for field_name in self.register_index_changed:
            form_field = self.form.find_field(field_name)
            if form_field is None:
                self.logger.debug(
                    f"Skipping registration of Slot {field_name}.update_field for "
                    + "index_changed Signal because field does not exist"
                )
                continue

            # noinspection PyTypeChecker
            form_widget = form_field.widget
            if not hasattr(form_widget, "update_field"):
                raise NotImplementedError(
                    f"The widget {form_widget} must have the update_field() method"
                )
            # noinspection PyUnresolvedReferences
            self.index_changed.connect(form_widget.update_field)
            self.logger.debug(
                f"Registered Slot {form_widget.name}.update_field for "
                + "index_changed Signal"
            )

    @Slot()
    def on_update_file(self, file: str) -> None:
        """
        Updates the stored file.
        :param file: The text set in the url field.
        :return: None
        """
        self.logger.debug(
            "Running on_update_file Slot because file changed from "
            + get_signal_sender(self)
        )

        # store the new values
        self.value = file
        self.full_file = self.sanitise_file(file)

        # show relevant (disabled) field, even if the file does not exist
        self.file_ext = ""
        if file is not None:
            _, self.file_ext = os.path.splitext(file)

        self.logger.debug("Completed on_update_file Slot")

    @Slot()
    def on_open_file(self) -> None:
        """
        Opens the table file externally.
        :return: None
        """
        # noinspection PyBroadException
        try:
            # ensure that the path is properly encoded
            file = os.path.normpath(self.full_file)
            self.logger.debug(f"Opening file {file}")
            os.startfile(file)
        except Exception:
            self.logger.debug(f"Failed to open because: {traceback.print_exc()}")
            QMessageBox().critical(
                self,
                "Cannot open the file",
                "An error occurred while trying to open the file",
            )

    @Slot()
    def on_browse_table_file(self) -> None:
        """
        Browse for a table new file. If a file is selected, this is added to the text
        field.
        :return: None
        """
        self.logger.debug("Opening file dialog")
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        files_filter = "CSV (*.csv);; Text (*.txt);; Excel (*.xls *.xlsx *.xlsm);; "
        files_filter += "HDF5 (*.h5)"
        file_dialog.setNameFilter(files_filter)

        file_dialog.exec()
        files = file_dialog.selectedFiles()
        if len(files) > 0:
            value = files[0]
            self.logger.debug(f"Selected {value}")
            self.line_edit.setText(value)

    @Slot()
    def on_reload_click(self) -> None:
        """
        Reloads the data stored by the widget (table, file, extension, etc.) when the
        Reload button is clicked.
        :return: None
        """
        self.logger.debug(f"Called on_reload_click Slot from {get_signal_sender(self)}")
        self.on_reload_all_data(self.full_file)
        self.logger.debug("Completed on_reload_click Slot")

    @Slot()
    def on_table_reload(self) -> None:
        """
        Reloads the table.
        :return:
        """
        self.logger.debug(
            f"Running on_table_reload Slot from {get_signal_sender(self)}"
        )
        self.load_table_data()
        self.logger.debug("Completed on_table_reload Slot")

    @Slot(str)
    def on_reload_all_data(self, file: str) -> None:
        """
        Updates the table and other widget data. This is called to populate the
        widget the first time and when data need to be reloaded (Reload button
        is clicked or file is changed).
        :param file: The text set in the url field.
        :return: None
        """
        self.logger.debug(
            f"Running on_reload_all_data Slot with file {file} from "
            + get_signal_sender(self)
        )

        # init
        self.field.clear_message()
        self.open_button.setDisabled(True)

        # read the file and update the table
        self.load_table_data()

        # show/hide the fields depending on the file type
        self.toggle_fields()

        # if field is empty do not show any message
        if self.value is None:
            return

        # table file does not exist
        if self.full_file is None and self.line_edit.text() != "":
            message = "The table file does not exist"
            self.logger.debug(message)
            self.field.set_error(message)
        elif self.file_ext != "" and self.file_ext not in self.supported_extensions:
            message = f"The file extension '{self.file_ext}' is not supported"
            self.logger.debug(message)
            self.field.set_error(message)
        elif self.table_parse_error:
            self.field.set_error(
                "Cannot parse the file. Try changing the options below"
            )
        else:
            self.open_button.setDisabled(False)

            # if the path is absolute convert to relative if possible
            if file is not None and os.path.isabs(file):
                rel_path = self.model_config.path_to_relative(file, False)
                # file is outside the model configuration folder
                if ".." in rel_path:
                    self.field.set_warning(
                        "It is always recommended to place the table file in the same "
                        + "folder as the model configuration file"
                    )
                else:
                    self.line_edit.blockSignals(True)
                    self.line_edit.setText(rel_path)
                    self.value = rel_path
                    self.line_edit.blockSignals(False)

        self.logger.debug("Completed on_reload_all_data Slot")

    def load_table_data(self) -> None:
        """
        Loads the table and stores error flags if the file cannot be loaded.
        :return: None.
        """
        self.logger.debug("Running load_data_table()")
        self.table = None
        self.table_parse_error = False

        if self.full_file is not None:
            # try parsing the table
            # noinspection PyBroadException
            try:
                if self.file_ext == ".csv" or self.file_ext == ".txt":
                    args = {}
                    for name in self.csv_fields:
                        field = self.form.find_field(name)
                        if field is not None:
                            args[name] = field.value()
                    args["low_memory"] = True
                    self.logger.debug(
                        f"Opening CSV file {self.full_file} using: {args}"
                    )
                    self.table = read_csv(self.full_file, **args)
                elif self.file_ext in [".xls", ".xlsx", ".xlsm"]:
                    args = {}
                    for name in self.excel_fields:
                        field = self.form.find_field(name)
                        if field is not None:
                            args[name] = field.value()
                    self.logger.debug(
                        f"Opening Excel file {self.full_file} using: {args}"
                    )
                    self.table = read_excel(self.full_file, **args)
                elif self.file_ext == ".h5":
                    args = {}
                    for name in self.hdf_fields:
                        field = self.form.find_field(name)
                        if field is not None:
                            args[name] = field.value()
                    self.logger.debug(f"Opening H5 file {self.full_file} using: {args}")
                    self.table = read_hdf(self.full_file, **args)
                    # remove built-in indexes and set them via attrs
                    # for H5 file, index names cannot be changed
                    index_names = reset_pandas_index_names(self.table)
                    self.logger.debug(f"Resetting built-in indexes: {index_names}")
                    set_table_index(self.table, index_names)

                if self.file_ext not in self.supported_extensions:
                    self.logger.debug(f"Extension '{self.file_ext}' not supported")
                    raise ValueError
            except Exception:
                self.logger.debug(
                    f"Cannot parse the file due to Exception: {traceback.print_exc()}"
                )
                self.table_parse_error = True
        else:
            self.logger.debug("The table file is not valid")

        self.logger.debug(f"DataFrame is\n {self.table}")
        self.logger.debug("Emitting updated_table Signal")
        # noinspection PyUnresolvedReferences
        self.updated_table.emit()

    def toggle_fields(self) -> None:
        """
        Shows or hides additional fields, based on the file extension, to properly
        parse the table file.
        :return: None
        """
        hide = list(
            set(
                self.csv_fields
                + self.excel_fields
                + self.hdf_fields
                + self.common_field
            )
        )
        show = []

        # on parse error, show fields to let user change the reader options
        if self.file_ext in self.supported_extensions and (
            self.table is not None or self.table_parse_error is True
        ):
            if self.file_ext in [".csv", ".txt"]:
                hide = self.excel_fields + self.hdf_fields
                show = self.csv_fields + self.common_field
            elif self.file_ext in [".xls", ".xlsx", ".xlsm"]:
                hide = self.csv_fields + self.hdf_fields
                show = self.excel_fields + self.common_field
            elif self.file_ext == ".h5":
                # index_col not used because index is set on DataFrame. parse_dates
                # not used because data types are defined in the DataFrame
                hide = self.csv_fields + self.excel_fields + self.common_field
                show = self.hdf_fields

        # show/hide the fields
        self.logger.debug(f"Hiding fields: {', '.join(hide)}")
        [
            self.form.change_field_visibility(
                name, show=False, clear_message=False, throw_if_missing=False
            )
            for name in hide
        ]

        self.logger.debug(f"Showing fields: {', '.join(show)}")
        [
            self.form.change_field_visibility(
                name, show=True, clear_message=False, throw_if_missing=False
            )
            for name in show
        ]

    def get_value(self) -> str:
        """
        Returns the form field value.
        :return: The form field value.
        """
        self.logger.debug(f"Fetching field value {self.value}")
        return self.value

    def get_default_value(self) -> str:
        """
        Returns the default value for the widget, when the value is not set.
        :return: The default value.
        """
        return ""

    def sanitise_file(self, file: str) -> str | None:
        """
        Sanitises the path to the file.
        :param file: The file from the input.
        :return: The sanitised path to the file, None if the file does not exist.
        """
        if file == "" or file is None:
            return None

        file = self.model_config.normalize_file_path(file)
        self.logger.debug(f"Converting file to absolute path {file}")
        if self.model_config.does_file_exist(file):
            return file
        else:
            self.logger.debug("The file does not exist")

    def reset(self) -> None:
        """
        Resets the widget. This empties the URL field and emits the updated_table Slot
        to force all the dependant fields to reset. The self.line_edit.textChanged
        Signal does emit the file_changed Signal and then the updated_table Signal only
        if the field is not empty when it is emptied.
        :return: None
        """
        # block signals to avoid emission of file_changed Signal
        # updated_table is manually triggered
        self.blockSignals(True)
        self.line_edit.setText("")
        self.blockSignals(False)

        # noinspection PyUnresolvedReferences
        self.updated_table.emit()

    def validate(self, name: str, label: str, value: str) -> Validation:
        """
        Checks that the file url is valid.
        :param name: The field name.
        :param label: The field label.
        :param value: The field label.
        :return: The Validation instance. The validation attribute is True, if the
        field contains an existing file and the table is valid.
        """
        self.logger.debug("Validating field")
        if self.table is not None:
            self.logger.debug("Validation passed")

            return Validation()

        self.logger.debug("Validation failed")
        return Validation("The file must exist and contain a supported and valid table")
