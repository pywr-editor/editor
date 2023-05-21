from typing import Any

import PySide6
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt


class AbstractAnnualValuesModel(QAbstractTableModel):
    def __init__(
        self,
        label: str,
        label_values: list[str] = None,
        values: list[float | int] = None,
    ):
        """
        Initialises the model.
        :param label: The name of the first column.
        :param label_values: The first column values. If None, the row number will be
        used.
        :param values: The list of values.
        """
        super().__init__()
        self.total_values = len(values)
        if values is None:
            self.values = [0] * (self.total_values + 1)
        else:
            # force values to float so that QSpinBox uses decimal places
            self.values = list(map(float, values))

        self.label = label
        self.label_values = label_values
        if self.label_values is None:
            self.label_values = list(range(1, self.total_values + 2))

    def data(
        self,
        index: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex,
        role: int = ...,
    ) -> Any:
        """
        Handles the data.
        :param index: The item index.
        :param role: The item role.
        :return: The item key or value.
        """
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                return self.label_values[index.row()]
            else:
                return self.values[index.row()]

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
            if section == 0:
                return self.label
            elif section == 1:
                return "Value"

    def rowCount(
        self,
        parent: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex = ...,
    ) -> int:
        """
        Provides the total number of rows.
        :param parent: The parent.
        :return: The row count.
        """
        return len(self.values)

    def columnCount(
        self,
        parent: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex = ...,
    ) -> int:
        """
        Provides the total number of columns.
        :param parent: The parent.
        :return: The column count.
        """
        return 2

    def setData(
        self,
        index: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex,
        value: Any,
        role: int = ...,
    ) -> bool:
        """
        Updates the data
        :param index: The table index being changed.
        :param value: The new value.
        :param role: The role.
        :return: True on success, False otherwise.
        """
        if role == Qt.ItemDataRole.EditRole:
            if not self.checkIndex(index):
                return False
            self.values[index.row()] = value
            # noinspection PyUnresolvedReferences
            self.dataChanged.emit(index.row(), index.column())

            return True

        return False

    def flags(
        self,
        index: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex,
    ) -> PySide6.QtCore.Qt.ItemFlag:
        """
        Handles the item flags to make each cell editable.
        :param index: The item index.
        :return: The item flags.
        """
        # prevent change of labels
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled
        else:
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled
