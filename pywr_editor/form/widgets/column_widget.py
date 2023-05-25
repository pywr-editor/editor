from pandas import DataFrame
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import (
    FormField,
    FormWidget,
    SourceSelectorWidget,
    TableSelectorWidget,
    UrlWidget,
    Validation,
)
from pywr_editor.utils import Logging, are_columns_valid, get_columns, get_signal_sender
from pywr_editor.widgets import ComboBox


class ColumnWidget(FormWidget):
    def __init__(
        self, name: str, value: str, parent: FormField, optional: bool = False
    ):
        """
        Initialises the widget to provide the list of the table columns. The field
        gets the data from the TableSelectorWidget. NOTE: H5 files are not supported
        for ConstantParameter (i.e. read_hdf does not support "index_col" to set the
        data frame index).
        :param name: The field name.
        :param value: The value set for the column.
        :param parent: The parent widget.
        :param optional: Whether the field is optional. Default to False.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")

        super().__init__(name, value, parent)
        self.wrong_column = False
        self.init = True
        self.optional = optional

        # columns list
        self.combo_box = ComboBox()
        self.combo_box_model = self.combo_box.model()

        # global layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

        # populate fields
        self.form.register_after_render_action(self.after_field_render)

    def after_field_render(self) -> None:
        """
        Populates the widget after the entire form is rendered to access to other form
        fields.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")

        # populate field for the first time
        self.logger.debug("Populating widget")
        self.on_populate_field()

        # update the internal value when the selected sheet name changes
        self.logger.debug("Connecting currentTextChanged Slot")
        # noinspection PyUnresolvedReferences
        self.combo_box.currentTextChanged.connect(self.on_update_value)
        self.init = False

    @property
    def table(self) -> DataFrame | None:
        """
        Returns the table used for the parameter. The table is loaded from the
        TableSelectorWidget or UrlWidget depending on the selected source.
        :return: The table, if the table is available. None otherwise.
        """
        # noinspection PyTypeChecker
        value_source_field = self.form.find_field("source")
        selected_source = value_source_field.value()
        # noinspection PyTypeChecker
        value_source_widget: SourceSelectorWidget = value_source_field.widget

        # dataframe from the table set in the table field
        if selected_source == value_source_widget.labels["table"]:
            # noinspection PyTypeChecker
            table_field: TableSelectorWidget = self.form.find_field("table").widget
            self.logger.debug("Table loaded from TableSelectorWidget")
        # dataframe from the table set in the url field
        elif selected_source == value_source_widget.labels["anonymous_table"]:
            # noinspection PyTypeChecker
            table_field: UrlWidget = self.form.find_field("url").widget
            self.logger.debug("Table loaded from UrlWidget")
        else:
            self.logger.debug("The table cannot be fetched")
            return None
        return table_field.table

    def sanitise_value(self, value: str | int) -> str | int | bool:
        """
        Sanitises the value and return the selected column.
        :param value: The value to sanitise.
        :return: The selected column name or False if the column name is invalid.
        """
        self.logger.debug(f"Sanitising value {value}")
        self.wrong_column = False
        selected_col_name = False
        table = self.table
        columns = get_columns(table)

        # table is not available or columns are not valid
        if are_columns_valid(table) is False:
            self.logger.debug(
                "The table is not available or is empty. Value not changed"
            )
            selected_col_name = value
        else:
            # handle different value types for the selected columns (as string or int)
            # ComboBox returns "None" if not item is selected
            if value in ["", "None"] or value is False:
                self.logger.debug("Value not set")
            # this is also handles when column key is not present in dictionary
            elif isinstance(value, (int, str)) is False:
                self.logger.debug(
                    f"The selected column is of wrong type '{type(value)}' instead of "
                    + "int or str"
                )
                selected_col_name = ""
            else:
                if value not in columns:
                    self.wrong_column = True
                    self.logger.debug(
                        f"The provided column name '{value}' does not exist in "
                        + "the table"
                    )
                else:
                    self.logger.debug(f"Using final value: '{selected_col_name}'")
                    selected_col_name = value

        return selected_col_name

    @Slot()
    def on_update_value(self, selected_column: str) -> None:
        """
        Stores the last selected value when the field changes.
        :param selected_column: The selected item in the QComboBox.
        :return: None
        """
        self.logger.debug(
            f"Running on_update_value Slot with value {selected_column} from "
            + get_signal_sender(self)
        )
        self.field.clear_message(message_type="warning")
        # ComboBox always returns a string - convert selected column to
        # original type
        type_conv = self.combo_box.currentData()
        self.value = self.sanitise_value(selected_column)
        if type_conv and self.value is not None:
            self.value = type_conv(selected_column)

        self.logger.debug(f"Updated field value to '{self.value}'")
        self.logger.debug("Completed on_update_value Slot")

    @Slot()
    def update_field(self) -> None:
        """
        Slots triggered to update the field. This is registered by the URL widget.
        :return: None
        """
        # when form is initialises, UrlWidget registers index_changed Slots, then
        # IndexColWidget inits and emits index_changed before ColWidget is initialised.
        # Prevent this behaviour (it is wrong) by ignoring the Signal before this
        # widget is initialised.
        if self.init is True:
            self.logger.debug(
                "Skipping update_field Slot when index changed. Widget not initialised"
                + " yet"
            )
            return

        self.logger.debug(
            "Running update_field Slot because table changed - "
            + get_signal_sender(self)
        )
        self.on_populate_field()
        self.logger.debug("Completed update_field Slot")

    @Slot()
    def on_populate_field(self) -> None:
        """
        Populates the ComoBox with the data from the table.
        :return: None
        """
        self.logger.debug(
            f"Running on_populate_field Slot from {get_signal_sender(self)}"
        )

        # empty the fields and disable the component
        self.logger.debug("Resetting widget")
        # prevent setCurrentText methods of ComboBox from triggering update Slot
        self.combo_box.blockSignals(True)

        # clear field and model
        self.combo_box.setEnabled(False)
        self.combo_box.clear()
        # self.combo_box_model.clear()
        self.field.clear_message(message_type="warning")
        # restore model signals for addItems call below
        self.combo_box.model().blockSignals(False)
        # do not use setCurrentText as lineEdit is not used
        self.combo_box.addItems(["None"])

        table = self.table
        columns = get_columns(table)
        self.value = self.sanitise_value(self.value)

        # table cannot be parsed or not available
        if table is None:
            self.logger.debug(
                "The table is not available and columns cannot be fetched"
            )
        # Empty table (Excel spreadsheets are still parsed but may have no columns)
        elif len(columns) == 0:
            self.field.set_warning("The table does not contain any column")
            self.logger.debug("Keeping field disabled with warning")
        # populate the field and enabled it
        else:
            items = sorted(list(columns))
            self.logger.debug(f"Filling field with: {', '.join(map(str, items))}")
            for col in items:
                # force to string and store type
                self.combo_box.addItem(str(col), type(col))
            self.combo_box.setEnabled(True)

            if self.value is False:
                self.logger.debug(
                    "No item is selected because the passed value is not valid"
                )

            if self.wrong_column:
                self.field.set_warning(
                    f"The column '{self.value}', currently set in the model "
                    "configuration file, does not exist in the table. Please "
                    "select another name"
                )
            elif self.value is not False:
                self.logger.debug(f"Selecting column '{self.value}'")
                self.combo_box.setCurrentText(str(self.value))

        self.combo_box.blockSignals(False)

        self.logger.debug("Completed on_populate_field Slot")

    def get_value(self) -> str | None:
        """
        Returns the selected column.
        :return: The column or none if the selection is invalid.
        """
        table = self.table
        if are_columns_valid(table) is False or self.value is False or self.value == "":
            return None
        return self.value

    def validate(
        self,
        name: str,
        label: str,
        value: str,
    ) -> Validation:
        """
        Validates the field. Validation fails if value is False or empty or the columns
        ar enot valid (the file does not exist, is invalid or has no content).
        :param name: The field name.
        :param label: The field label.
        :param value: The field value from self.get_value().
        :return: The Validation instance.
        """
        self.logger.debug("Validating field")

        if self.optional:
            self.logger.debug("Field is optional. Validation passed")
            return Validation()

        if (
            value is None
            or value == ""
            or value is False
            or are_columns_valid(self.table) is False
        ):
            self.logger.debug("Validation failed")
            return Validation("You must select a column from the list")

        self.logger.debug("Validation passed")
        return Validation()
