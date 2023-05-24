from typing import TYPE_CHECKING, Any

from pandas import DataFrame
from PySide6.QtCore import QModelIndex, Slot
from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import FormCustomWidget, Validation
from pywr_editor.utils import (
    Logging,
    default_index_name,
    find_existing_columns,
    get_columns,
    get_index_names,
    get_signal_sender,
    set_table_index,
)
from pywr_editor.widgets import CheckableComboBox

if TYPE_CHECKING:
    from pywr_editor.form import FormField, UrlWidget

"""
 This widget is used for the index_col and
 parse_dates fields and provides a multi-selection
 ComboBox to select table columns.
"""


class AbstractColumnsSelectorWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: str | int | list,
        parent: "FormField",
        log_name: str,
        is_index_selector: bool,
    ):
        """
        Initialises the widget. NOTE: this field is only used when the user is setting
        up an anonymous table by providing the file path in the URL field. When
        self.is_index_selector is True and for H5 files, the widget is filled but
        disabled because the DataFrame index cannot be changed.
        :param name: The field name.
        :param value: The current selected column.
        :param parent: The parent widget.
        :param is_index_selector: Whether the widget acts as selector for DataFrame
        index. When True, when one or more columns are selected, the DataFrame index
        gets set.
        :param log_name: The name to use in the logger.
        """
        self.logger = Logging().logger(log_name)
        self.logger.debug(f"Loading widget with value {value}")

        super().__init__(name, value, parent)

        self.is_index_selector = is_index_selector
        self.value = self.sanitise_value(value)
        self.wrong_columns: list[str] = []

        # field that defines the type of index_col (int, str or list of int or str)
        self.combo_box = CheckableComboBox()
        self.combo_box.setObjectName(f"{name}_checkable_combo_box")
        self.combo_box_model = self.combo_box.model()

        # global layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")

        # populate field for the first time
        self.logger.debug("Populating widget")
        self.on_populate_field()

        # update the internal value when the selected sheet name changes
        self.logger.debug("Connecting currentTextChanged Slot")
        # noinspection PyUnresolvedReferences
        self.combo_box_model.dataChanged.connect(self.on_update_value)

    @Slot()
    def on_populate_field(self) -> None:
        """
        Populates the ComoBox with the column names.
        :return: None
        """
        self.logger.debug(
            f"Running on_populate_field Slot from {get_signal_sender(self)}"
        )
        self.logger.debug("Resetting widget")

        # clear field and model
        self.setEnabled(False)
        self.combo_box.clear()
        self.field.clear_message(message_type="warning")
        self.value = self.sanitise_value(self.value)
        columns = self.columns

        # table cannot be parsed or not available (user is not configuring an anonymous
        # table)
        if columns is None:
            self.logger.debug(
                "The table is not available and columns cannot be fetched"
            )
        # Empty table (Excel spreadsheets are still parsed but may have no columns)
        elif len(columns) == 0:
            self.logger.debug(
                "The table does not contain any column. Keeping field disabled with "
                + "warning"
            )
            self.field.set_warning("The table does not contain any column")
        else:
            self.logger.debug(f"Filling field with: {', '.join(map(str,columns))}")
            # noinspection PyTypeChecker
            url_form_widget: "UrlWidget" = self.form.fields["url"].widget
            # H5 files already contain DataFrame object (index is already set and
            # dates already parsed)
            if url_form_widget.file_ext == ".h5":
                self.logger.debug("File is H5; leaving field as disabled")
                columns = []
                self.value = []
            else:
                self.setEnabled(True)

            # fill the field and select the columns
            self.combo_box.addItems(columns)

            # set selection use column numbers
            indexes = [columns.index(col_name) for col_name in self.value]
            self.set_table_index()

            # log if index is an empty list
            if not indexes:
                self.logger.debug("No items are selected. No valid columns found")

            for col_index in indexes:
                self.logger.debug(
                    f"Selecting column {columns[col_index]} with index #{col_index}"
                )
                # changes of index is signalled by self.set_table_index()
                self.combo_box.check_items(col_index, emit_signal=False)

            # some provided column names or indexes may not exist
            if len(self.wrong_columns) > 0:
                self.logger.debug(
                    "The following columns do no exist in the file: "
                    + " ".join(self.wrong_columns)
                )
                self.field.set_warning(
                    "The following columns, currently set in the model config file, "
                    + "do not exist in the table file: "
                    + ", ".join(self.wrong_columns)
                )

        self.logger.debug("Completed on_populate_field Slot")

    @Slot()
    def update_field(self) -> None:
        """
        Slots triggered to update the field. This is registered by the URL widget.
        :return: None
        """
        self.logger.debug(
            "Running update_field Slot because table changed - "
            + get_signal_sender(self)
        )
        self.on_populate_field()
        self.logger.debug("Completed update_field Slot")

    def sanitise_value(self, value: str | int | list) -> list[str] | bool:
        """
        Sanitises the value. If the DataFrame columns are available and the value is a
        column number, this will be converted to a column name for consistency.
        Moreover, if the value is a string or integer, it will be converted to a list
        to handle multi-indexes. This also updates self.wrong_columns with the wrong
        column names or indexes.
        :param value: The value to sanitise.
        :return: The list of selected column names or False if the column name or
        number is invalid.
        """
        self.logger.debug(f"Sanitising value '{value}'")
        selected_col_name = []
        self.wrong_columns = []
        columns = self.columns

        # table is not available or columns are not valid
        if self.are_columns_valid is False:
            self.logger.debug(
                "The table is not available or is empty. Value not changed"
            )
            selected_col_name = value
        else:
            self.logger.debug(
                f"Found the following columns: {', '.join(map(str,columns))}"
            )

            # for H5 file, use the built-in index as it does not come form index_col key
            if self.is_h5_table and self.is_index_selector:
                selected_col_name = get_index_names(self.table)
                # No index is selected
                if selected_col_name == [default_index_name]:
                    selected_col_name = []
                self.logger.debug(
                    f"Table is from H5 file. Index forced to {selected_col_name}"
                )
            # CheckableComboBox returns "None" if not item is selected
            elif (
                value in ["", "None"]
                or value is None
                or value is False
                or (isinstance(value, list) and len(value) == 0)
            ):
                self.logger.debug("Index names not set")
            # handle different value types for the selected columns (as string or int)
            else:
                # Convert value to list
                if not isinstance(value, list):
                    # When updating field, ComboBox widget returns a string with
                    # comma-separated field
                    if isinstance(value, str) and "," in value:
                        self.logger.debug("Converting comma-separated value to a list")
                        value = value.split(", ")
                    else:
                        self.logger.debug("Converting value to a list")
                        value = [value]

                # Handle different types
                try:
                    (
                        selected_col_name,
                        self.wrong_columns,
                    ) = find_existing_columns(self.table, value, include_index=True)
                    self.wrong_columns = list(map(str, self.wrong_columns))
                    if len(self.wrong_columns) > 0:
                        self.logger.debug(
                            "Wrong column names detected: "
                            + ", ".join(self.wrong_columns)
                        )
                    self.logger.debug(
                        f"Using final value: {', '.join(selected_col_name)}"
                    )
                except TypeError:
                    self.logger.debug(f"{value} is not a valid column")
                    pass

        return selected_col_name

    def set_table_index(self) -> bool | None:
        """
        Set the index on the table. This method does nothing if self.is_index_selector
        is False.
        :return: True if the new index are set, None otherwise.
        """
        if self.is_index_selector is False:
            return

        self.logger.debug("Preparing to set index on table")
        if self.is_h5_table:
            self.logger.debug("File is H5; index cannot be set")
            return

        new_index_names = self.value

        flag = set_table_index(self.table, new_index_names)
        if flag is False:
            self.logger.debug("Table is not available")
            return None
        else:
            self.logger.debug(f"Stored new indexes in table '{self.value}'")
            self.logger.debug("Emitting index_changed Signal")
            return True

    @Slot()
    def on_update_value(self, selected_columns: QModelIndex) -> None:
        """
        Stores the last selected value when the field changes.
        :param selected_columns: The selected item or items in the QComboBox. This is a
        string with comma-separated column names.
        :return: None
        """
        selected_columns = self.combo_box.checked_items()
        self.logger.debug(
            f"Running on_update_value Slot with value {selected_columns} from "
            + get_signal_sender(self)
        )
        self.field.clear_message(message_type="warning")
        self.value = self.sanitise_value(selected_columns)
        self.logger.debug(f"Updated field value to '{self.value}'")
        # when user check or uncheck an item, update the table index
        flag = self.set_table_index()

        if flag is True:
            # noinspection PyTypeChecker
            url_form_widget: "UrlWidget" = self.form.fields["url"].widget
            self.logger.debug("Emitting index_changed Signal")
            url_form_widget.index_changed.emit()

        self.logger.debug("Completed on_update_value Slot")

    @property
    def table(self) -> DataFrame | None:
        """
        Returns the DataFrame.
        :return: The DataFrame.
        """
        # noinspection PyTypeChecker
        url_form_field: "UrlWidget" = self.form.fields["url"].widget
        return url_form_field.table

    @property
    def is_h5_table(self) -> bool:
        """
        Checks if the DataFrame comes from a H5 file.
        :return: True if the table comes from a H5 file, False otherwise.
        """
        # noinspection PyTypeChecker
        url_form_field: "UrlWidget" = self.form.fields["url"].widget
        return url_form_field.file_ext == ".h5"

    @property
    def columns(self) -> list[str] | None:
        """
        Returns all the DataFrame columns (including the indexes).
        :return: The list of column names or None if the table or columns are not
        available.
        """
        # fetch columns
        available_columns = get_columns(self.table, include_index=True)
        return available_columns

    @property
    def are_columns_valid(self) -> bool:
        """
        Checks if the table columns are valid. Columns are not valid if the valid is
        not available or when the table is empty.
        :return: True if the columns are valid, False otherwise.
        """
        columns = self.columns
        return columns is not None and len(columns) > 0

    def get_value(self) -> list[str]:
        """
        Returns the value.
        :return: The set value.
        """
        # return empty list if the file/table is not available or table is not valid or
        # there are not selected columns
        if self.are_columns_valid is False or self.value is False:
            return []

        # for anonymous index, returns None
        if (
            self.is_index_selector is True
            and isinstance(self.value, str)
            and self.value == default_index_name
        ):
            return []

        return self.value

    def validate(
        self,
        name: str,
        label: str,
        value: list[str] | None,
    ) -> Validation:
        """
        The field is not mandatory. When the widget is used to set a table index, the
        value can be None to use the anonymous (numeric) index.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value from self.get_value().
        :return: The Validation instance.
        """
        return Validation()

    def after_validate(self, form_dict: dict[str, Any], form_field_name: str) -> None:
        # convert names to int with Excel - Pandas does not support strings when
        # setting an index as column
        if self.is_index_selector:
            url_form_field: "UrlWidget" = self.form.fields["url"].widget
            if url_form_field.file_ext and "xls" in url_form_field.file_ext:
                form_dict[self.name] = [self.columns.index(col) for col in self.value]
