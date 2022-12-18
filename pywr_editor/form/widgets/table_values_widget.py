import traceback
import PySide6
from itertools import groupby
from PySide6.QtAxContainer import QAxObject
from PySide6.QtCore import Slot, Qt, QCoreApplication
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QVBoxLayout,
    QStyledItemDelegate,
    QHBoxLayout,
    QMessageBox,
    QHeaderView,
    QWidget,
)
from pywr_editor.widgets import (
    TableView,
    PushButton,
    DoubleSpinBox,
    PushIconButton,
)
from pywr_editor.form import TableValuesModel, FormCustomWidget, FormValidation
from pywr_editor.utils import (
    get_signal_sender,
    Logging,
    is_excel_installed,
    move_row,
)

"""
 Displays a widget with a table with the variable
 names in the table header and their values in the
 table rows. Values can be added, deleted or edited
 with the dedicated buttons.
"""


class TableValuesWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: dict[str, list[int | float]] | None,
        parent=None,
        show_row_numbers: bool = False,
        row_number_from_zero: bool = False,
        row_number_label: str = "Row",
        min_total_values: int | None = None,
        exact_total_values: int | None = None,
        enforce_bounds: bool = False,
        upper_bound: float = pow(10, 6),
        lower_bound: float = pow(10, -6),
        precision: int = 4,
        use_integers_only: bool = False,
        scientific_notation: bool = False,
    ):
        """
        Initialises the widget to show tabled values.
        :param name: The field name.
        :param value: A dictionary with the variable name as key as its values as
        value.
        :param parent: The parent widget.
        :param show_row_numbers: Shows the number of the row in the table.
        Default to False.
        :param row_number_from_zero: Starts the row number from zero when
        show_row_numbers is True. Default to False.
        :param row_number_label: The column label for the row numbers. Default to Row.
        :param min_total_values: The minimum total values each variable must have.
        Default to None to avoid any initial check and form validation.
        :param exact_total_values: When provided in place of min_total_values, each
        variable must have the exact provided number of items. Default to None to
        avoid any initial check and form validation.
        :param lower_bound: The allowed minimum number. Default to -10^6
        :param upper_bound: The allowed maximum number. Default to 10^6
        :param enforce_bounds: Returns a warning if one number is outside the lower and
        upper bounds.
        :param precision: The precision. Default to 4.
        :param use_integers_only: Force the widget to use integers only. Precision is
        set to 0 and warning is shown if floats are provided. Default to False.
        :param scientific_notation: Enable scientific notation. Default to False.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget {name} with value {value}")
        self.warning_message = None
        self.enforce_bounds = enforce_bounds
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.show_row_numbers = show_row_numbers
        self.min_total_values = min_total_values
        self.exact_total_values = exact_total_values
        self.use_integers_only = use_integers_only

        super().__init__(name=name, value=value, parent=parent)

        if not isinstance(value, dict):
            raise ValueError(
                f"value must be a valid dictionary, but {value} was given"
            )

        if exact_total_values and min_total_values:
            raise ValueError(
                "You cannot provide exact_total_values and "
                "min_total_values at the same time"
            )
        if use_integers_only:
            precision = 0

        # Table
        self.values, self.warning_message = self.sanitise_value(value)
        self.logger.debug(f"Using {self.values}")

        self.model = TableValuesModel(
            labels=list(value.keys()),
            values=self.values,
            show_row_numbers=show_row_numbers,
            row_number_from_zero=row_number_from_zero,
            row_number_label=row_number_label,
        )
        # noinspection PyUnresolvedReferences
        self.model.dataChanged.connect(self.on_value_change)
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.connect(self.on_value_change)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.add_button = PushIconButton(
            icon=":misc/plus", label="Add", small=True
        )
        self.add_button.setToolTip("Add a new row to the table")
        # noinspection PyUnresolvedReferences
        self.add_button.clicked.connect(self.on_add_new_row)

        self.delete_button = PushIconButton(
            icon=":misc/minus", label="Delete", small=True
        )
        self.delete_button.setToolTip("Delete the selected row in the table")
        self.delete_button.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.delete_button.clicked.connect(self.on_delete_row)

        self.move_up = PushButton(label="Move up", small=True)
        self.move_up.setDisabled(True)
        self.move_up.setToolTip("Move the selected row up in the table")
        # noinspection PyUnresolvedReferences
        self.move_up.clicked.connect(self.on_move_up)

        self.move_down = PushButton(label="Move down", small=True)
        self.move_down.setDisabled(True)
        self.move_down.setToolTip("Move the selected row down in the table")
        # noinspection PyUnresolvedReferences
        self.move_down.clicked.connect(self.on_move_down)

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.move_up)
        self.button_layout.addWidget(self.move_down)
        self.button_layout.addStretch()

        if is_excel_installed():
            self.paste_button = PushIconButton(
                icon=":misc/paste", label="Paste from Excel", small=True
            )
            self.paste_button.setToolTip(
                "Paste data copied from a column from an Excel spreadsheet"
            )
            # noinspection PyUnresolvedReferences
            self.paste_button.clicked.connect(self.paste_from_excel)

            self.export_button = PushIconButton(
                icon=":misc/export", label="Export to Excel", small=True
            )
            self.export_button.setToolTip(
                "Create an Excel spreadsheet containing the data from the table above"
            )
            # noinspection PyUnresolvedReferences
            self.export_button.clicked.connect(self.export_to_excel)

            self.button_layout.addWidget(self.paste_button)
            self.button_layout.addWidget(self.export_button)

        # Table
        self.table = TableView(self.model, self.delete_button)
        self.table.setMaximumHeight(200)
        # resize first column with row numbers if shown
        if show_row_numbers:
            self.table.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.ResizeToContents
            )
        # customise the spin box limits and precision
        self.table.setItemDelegate(
            TableSpinBoxDelegate(
                scientific_notation=scientific_notation,
                upper_bound=upper_bound,
                lower_bound=lower_bound,
                precision=precision,
                parent=self,
            )
        )
        # noinspection PyUnresolvedReferences
        self.table.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )

        # hide header with one variable
        if len(self.model.labels) == 1 and show_row_numbers is False:
            self.table.horizontalHeader().hide()

        # Set layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)
        layout.addLayout(self.button_layout)

        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        self.form_field.set_warning_message(self.warning_message)

    @Slot()
    def on_value_change(self) -> None:
        """
        Enables the form button when the widget is updated.
        :return: None
        """
        self.form.save_button.setEnabled(True)

    def sanitise_value(
        self, value: dict[str, list[int | float]] | None
    ) -> [list[float | int], str | None]:
        """
        Sanitises the value.
        :param value: The value to sanitise. This is a dictionary with the variable
        name as key and its value as value.
        :return: The list of values and the warning message.
        """
        self.logger.debug(f"Sanitising value '{value}'")

        # check values
        message = None
        values = self.get_default_value()
        variable_values = list(value.values())
        allowed_types = (float, int) if not self.use_integers_only else int

        # value or any value in dictionary is None
        if value is None or any([v is None for v in variable_values]):
            self.logger.debug("Value is None")
        # values for all variables must be valid lists
        elif all(isinstance(v, list) for v in variable_values) is False:
            message = (
                "The values set in the model configuration must be all "
                + "valid lists"
            )
        # all list items must be numbers
        elif (
            all(
                [
                    all(
                        [
                            not isinstance(nested_value, bool)
                            and isinstance(nested_value, allowed_types)
                            for nested_value in nested_list
                        ]
                    )
                    for nested_list in variable_values
                ]
            )
            is False
        ):
            message = "The value in the model configuration can only contain "
            if self.use_integers_only:
                message += "integers"
            else:
                message += "numbers"
        # check bounds
        elif self.enforce_bounds and not all(
            [
                self.lower_bound <= v <= self.upper_bound
                for nested_list in variable_values
                for v in nested_list
            ]
        ):
            message = "One or more values are outside the allowed range"
        else:
            # all nested lists must have the same size. Pad the list with zeros
            if self._all_equal([len(v) for v in variable_values]) is False:
                max_length = max(
                    [len(nested_list) for nested_list in variable_values]
                )
                variable_values = [
                    nested_list
                    if len(nested_list) == max_length
                    else nested_list + [0] * (max_length - len(nested_list))
                    for nested_list in variable_values
                ]
                message = (
                    "The number of values must be the same for each variable. "
                    + "Some values were set to zero"
                )
            # check minimum total items requirement
            if self.min_total_values and any(
                [len(v) < self.min_total_values for v in variable_values]
            ):
                new_message = (
                    "The number of data points must be at least "
                    + f"{self.min_total_values}"
                )
                # concatenate messages
                if message is not None:
                    message = f"{message}. {new_message}"
                else:
                    message = new_message
            # check requirement for exact number of items - skip if list is empty
            elif self.exact_total_values and any(
                [
                    len(v) > 0 and len(v) != self.exact_total_values
                    for v in variable_values
                ]
            ):
                new_message = (
                    "The number of data points must exactly be "
                    + f"{self.exact_total_values}"
                )
                # concatenate messages
                if message is not None:
                    message = f"{message}. {new_message}"
                else:
                    message = new_message
            values = variable_values

        if message is not None:
            self.logger.debug(message)

        return values, message

    @staticmethod
    def _all_equal(iterable: list) -> bool:
        """
        Checks if all list items are the same.
        :param iterable: The list to check.
        :return Whether all items are the same.
        """
        g = groupby(iterable)
        return next(g, True) and not next(g, False)

    def get_value(self) -> dict[str, list[float | int]]:
        """
        Returns the values from the table.
        :return: A dictionary with the variable names as keys and their values as
        values.
        """
        value_dict = {}
        for vi, variable_name in enumerate(self.model.labels):
            value_dict[variable_name] = self.model.values[vi]

        return value_dict

    def get_default_value(self) -> list[list]:
        """
        The field default value.
        :return: None.
        """
        return [[] for _ in self.value.keys()]

    def reset(self) -> None:
        """
        Resets the widget. This sets all the values to zero in the table.
        :return: None
        """
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.values = self.get_default_value()
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    @Slot()
    def on_add_new_row(self) -> None:
        """
        Adds a new row in the table.
        :return: None
        """
        self.logger.debug(
            f"Running on_add_new_row Slot from {get_signal_sender(self)}"
        )
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()

        # Add a new row with zeros
        new_values = []
        for variable_values in self.model.values:
            new_values.append(variable_values + [0])
        self.model.values = new_values
        self.logger.debug(
            f"Added a new row. New size is {self.model.rowCount()}"
        )

        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

        # make last row editable
        # first column is not editable if self.show_row_numbers is True
        col_number = 0 if self.show_row_numbers is False else 1
        last_row = self.model.index(self.model.rowCount() - 1, col_number)
        if last_row.isValid():
            self.table.edit(last_row)

    @Slot()
    def on_delete_row(self) -> None:
        """
        Deletes the selected row.
        :return: None
        """
        self.logger.debug(
            f"Running on_delete_row Slot from {get_signal_sender(self)}"
        )
        indexes = self.table.selectedIndexes()
        row_indexes = [index.row() for index in indexes]

        # delete selected indexes for each variable
        new_values = []
        for ci, variable_values in enumerate(self.model.values):
            new_variable_values = [
                v
                for vi, v in enumerate(variable_values)
                if vi not in row_indexes
            ]
            new_values.append(new_variable_values)
            self.logger.debug(
                f"Updated '{self.model.labels[ci]}' to {new_variable_values}"
            )

        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.values = new_values
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()

    @Slot()
    def on_selection_changed(self) -> None:
        """
        Enable or disable action buttons based on the number of selected items.
        :return: None
        """
        self.logger.debug(
            f"Running on_selection_changed Slot from {get_signal_sender(self)}"
        )
        selection = self.table.selectionModel().selection()
        total_rows = self.table.model.rowCount()

        # enable the sorting buttons only when one item is selected
        if len(selection.indexes()) == 1:
            # enable/disable sorting buttons based on the selected row (for example,
            # if last row, move down button is disabled)
            selected_row = selection.indexes()[0].row() + 1
            self.move_up.setEnabled(selected_row != 1)
            self.move_down.setEnabled(selected_row != total_rows)
        else:
            self.move_up.setEnabled(False)
            self.move_down.setEnabled(False)

    @Slot()
    def on_move_up(self) -> None:
        """
        Moves a parameter up in the table.
        :return: None
        """
        self.logger.debug(
            f"Running on_move_up Slot from {get_signal_sender(self)}"
        )
        move_row(
            widget=self.table, direction="up", callback=self.move_row_in_model
        )

    @Slot()
    def on_move_down(self) -> None:
        """
        Moves a parameter down in the table.
        :return: None
        """
        self.logger.debug(
            f"Running on_move_down Slot from {get_signal_sender(self)}"
        )
        move_row(
            widget=self.table, direction="down", callback=self.move_row_in_model
        )

    def move_row_in_model(self, current_index: int, new_index: int) -> None:
        """
        Moves a model's item.
        :param current_index: The row index being moved.
        :param new_index: The row index the item is being moved to.
        :return: None
        """
        new_values = []
        for variable_values in self.model.values:
            new_values.append(
                variable_values.insert(
                    new_index, variable_values.pop(current_index)
                )
            )
        self.logger.debug(f"Moved index {current_index} to {new_index}")

    @Slot()
    def paste_from_excel(self) -> None:
        """
        Populates the model with data from the clipboard.
        :return: None
        """
        clipboard = QGuiApplication.clipboard()
        text = clipboard.text()
        self.logger.debug(f"Pasting data from clipboard {repr(text)}")
        data_points = None
        message = None

        # check if list contains number
        # noinspection PyBroadException
        try:
            # split columns and skip empty text
            data_points = [
                list(map(float, col_text.split("\t")))
                for col_text in clipboard.text().split("\n")
                if col_text
            ]
            # transpose data
            data_points = list(map(list, zip(*data_points)))
        except Exception:
            message = "The clipboard data must contain valid numbers"

        # check list size
        if message is None:
            self.logger.debug(f"Detected: {data_points}")
            if len(data_points) == 0:
                message = (
                    "The clipboard is empty. Please copy the data from an "
                    + "Excel spreadsheet"
                )
            elif len(data_points) != len(self.model.labels):
                message = (
                    f"The data must contain {len(self.model.labels)} columns, "
                    + f"but {len(data_points)} columns were detected"
                )
            elif self._all_equal([len(v) for v in data_points]) is False:
                message = "The data points must contain the same number of rows"

        if message is not None:
            self.logger.debug(message)
            QMessageBox.warning(
                self,
                "Warning",
                message,
                QMessageBox.StandardButton.Ok,
            )
            return

        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.values = data_points
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        # noinspection PyUnresolvedReferences
        self.model.dataChanged.emit([], [], [])
        self.logger.debug("Model updated")

    # noinspection PyTypeChecker
    @Slot()
    def export_to_excel(self) -> None:
        """
        Exports the data to an Excel spreadsheet.
        :return: None
        """
        self.logger.debug("Exporting data to Excel")
        # disable button
        self.export_button.setEnabled(False)
        button_text = self.export_button.text()
        self.export_button.setText("Exporting...")
        self.table.setFocus()
        QCoreApplication.processEvents()

        # add the workbook
        # noinspection PyBroadException
        try:
            excel = QAxObject("Excel.Application", self)
            work_books = excel.querySubObject("WorkBooks")
            work_books.dynamicCall("Add")
            work_book = excel.querySubObject("ActiveWorkBook")

            # rename the sheet
            work_sheets = work_book.querySubObject("Sheets")
            first_sheet = work_sheets.querySubObject("Item(int)", 1)
            param_name = self.form.find_field_by_name("name").value()
            if param_name is not None and param_name != "":
                first_sheet.setProperty("Name", param_name)

            # ignore column with row number
            if self.show_row_numbers:
                col_indexes = range(1, self.model.columnCount())
                header_col_indexes = range(0, self.model.columnCount() - 1)
            else:
                col_indexes = range(0, self.model.columnCount())
                header_col_indexes = col_indexes

            # header
            for col_idx in header_col_indexes:
                cell = first_sheet.querySubObject(
                    "Cells(int, int)", 1, col_idx + 1
                )
                cell.setProperty(
                    "Value", self.model.labels[col_idx].capitalize()
                )

            # values
            for row in range(0, self.model.rowCount()):
                for col in col_indexes:
                    index = self.model.index(row, col)
                    # ignore row number
                    if self.show_row_numbers:
                        col -= 1
                    cell = first_sheet.querySubObject(
                        "Cells(int, int)", row + 2, col + 1
                    )
                    cell.setProperty(
                        "Value",
                        self.model.data(index, Qt.ItemDataRole.DisplayRole),
                    )

            # show Excel
            excel.dynamicCall("SetVisible(bool)", True)
        except Exception:
            self.logger.debug(
                "An error occurred while exporting data to Excel: "
                + f"{traceback.print_exc()}"
            )
            QMessageBox.critical(
                self,
                "Error",
                "An error occurred while exporting the data to Excel",
                QMessageBox.StandardButton.Ok,
            )

        self.export_button.setEnabled(True)
        self.export_button.setText(button_text)

    def validate(
        self,
        name: str,
        label: str,
        value: dict[str, list[float | int]],
    ) -> FormValidation:
        """
        Checks that valid data points are provided.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value from self.get_value().
        :return: The FormValidation instance.
        """
        self.logger.debug("Validating field")

        first_key = list(value.keys())[0]
        # check minimum items requirement
        if (
            self.min_total_values
            and len(value[first_key]) < self.min_total_values
        ):
            name = "value" if self.min_total_values == 1 else "values"
            return FormValidation(
                validation=False,
                error_message="You must provide at least "
                + f"{self.min_total_values} {name}",
            )
        # check requirement for exact size of items
        elif (
            self.exact_total_values
            and len(value[first_key]) != self.exact_total_values
        ):
            return FormValidation(
                validation=False,
                error_message="You must provide exactly "
                + f"{self.exact_total_values} values",
            )

        return FormValidation(validation=True)


class TableSpinBoxDelegate(QStyledItemDelegate):
    def __init__(
        self,
        scientific_notation: bool,
        upper_bound: float,
        lower_bound: float,
        precision: int,
        parent: QWidget = None,
    ):
        """
        Initialises the delegate class.
        :param lower_bound: The allowed minimum number.
        :param upper_bound: The allowed maximum number.
        :param precision: The precision.
        :param scientific_notation: Enable scientific notation.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.scientific_notation = scientific_notation
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.precision = precision

    def createEditor(
        self,
        parent: PySide6.QtWidgets.QWidget,
        option: PySide6.QtWidgets.QStyleOptionViewItem,
        index: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex,
    ) -> PySide6.QtWidgets.QWidget:
        # extend range
        editor = DoubleSpinBox(
            scientific_notation=self.scientific_notation,
            upper_bound=self.upper_bound,
            lower_bound=self.lower_bound,
            precision=self.precision,
            parent=parent,
        )
        return editor
