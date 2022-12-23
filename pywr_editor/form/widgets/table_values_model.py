from typing import Any

import PySide6
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt


class TableValuesModel(QAbstractTableModel):
    def __init__(
        self,
        labels: list[str],
        values: list[list[float | int]],
        show_row_numbers: bool,
        row_number_from_zero: bool,
        row_number_label: str,
    ):
        """
        Initialises the model.
        :param labels: The list of column names.
        :param values: The list of values.
        :param show_row_numbers: Shows the number of the row in the table.
        :param row_number_from_zero: Starts the row number from zero.
        :param row_number_label: The column label for the row numbers.
        """
        super().__init__()
        if len(labels) != len(values):
            raise ValueError(
                "The number of columns must match then number of variables"
            )
        # init empty lists
        if values is None:
            values = [[] for _ in labels]
        # force to floats
        else:
            try:
                values = [list(map(float, var_values)) for var_values in values]
            except TypeError:
                values = [[] for _ in labels]

        self.labels = labels
        self.values = values
        self.show_row_numbers = show_row_numbers
        self.row_number_from_zero = row_number_from_zero
        self.row_number_label = row_number_label

    def data(
        self,
        index: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex,
        role: int = ...,
    ) -> Any:
        """
        Handles the data.
        :param index: The item index.
        :param role: The item role.
        :return: The item key or value.
        """
        if (
            role == Qt.ItemDataRole.DisplayRole
            or role == Qt.ItemDataRole.EditRole
        ):
            if index.isValid() is False:
                return

            # show row number
            if self.show_row_numbers and index.column() == 0:
                return (
                    index.row()
                    if self.row_number_from_zero
                    else (index.row() + 1)
                )

            # shift the column if needed
            col_number = index.column()
            if self.show_row_numbers:
                col_number -= 1

            try:
                return self.values[col_number][index.row()]
            except IndexError:
                return 0

    def headerData(
        self,
        section: int,
        orientation: PySide6.QtCore.Qt.Orientation,
        role: int = ...,
    ) -> Any:
        """
        Handles the header.
        :param section: The section id.
        :param orientation: The header orientation.
        :param role: The header role.
        :return: The column text.
        """
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            if self.show_row_numbers and section == 0:
                return self.row_number_label

            # shift the column if needed
            section_number = section
            if self.show_row_numbers:
                section_number -= 1

            return self.labels[section_number].capitalize()

    def rowCount(
        self,
        parent: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex = ...,
    ) -> int:
        """
        Provides the total number of rows.
        :param parent: The parent.
        :return: The row count.
        """
        # get the maximum length from all variables
        return max([len(var_values) for var_values in self.values])

    def columnCount(
        self,
        parent: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex = ...,
    ) -> int:
        """
        Provides the total number of columns.
        :param parent: The parent.
        :return: The column count.
        """
        if self.show_row_numbers:
            return len(self.labels) + 1
        return len(self.labels)

    def setData(
        self,
        index: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex,
        value: Any,
        role: int = ...,
    ) -> bool:
        """
        Updates the data. When self.show_row_numbers is True, the row labels in the
        first column cannot be modified.
        :param index: The table index being changed.
        :param value: The new value.
        :param role: The role.
        :return: True on success, False otherwise.
        """
        if role == Qt.ItemDataRole.EditRole:
            if not self.checkIndex(index):
                return False

            column_number = index.column()
            if self.show_row_numbers:
                column_number -= 1

            self.values[column_number][index.row()] = value
            # noinspection PyUnresolvedReferences
            self.dataChanged.emit(index.row(), index.column())

            return True

        return False

    def flags(
        self,
        index: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex,
    ) -> PySide6.QtCore.Qt.ItemFlag:
        """
        Handles the item flags to make each cell editable.
        :param index: The item index.
        :return: The item flags.
        """
        if self.show_row_numbers and index.column() == 0:
            return Qt.ItemFlag.ItemIsSelectable
        return (
            Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
        )
