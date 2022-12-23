from typing import Any

import PySide6
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt


class KeatingStreamsModel(QAbstractTableModel):
    def __init__(
        self,
        levels: list[list[float | None]],
        transmissivity: list[float | None],
    ):
        """
        Initialises the model.
        :param levels: The list of levels.
        :param transmissivity: The list of transmissivity coefficients.
        """
        super().__init__()

        self.levels = levels
        self.transmissivity = transmissivity

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
            # transmissivity
            if index.row() == self.rowCount() - 1:
                value = self.transmissivity[index.column()]
            else:
                value = self.levels[index.row()][index.column()]

            if value is None:
                return ""
            else:
                return str(value)

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
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return f"Level {section+1}"
            elif orientation == Qt.Orientation.Vertical:
                if section == self.rowCount() - 1:
                    return "Transmissivity"
                else:
                    return f"Stream {section+1}"

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
        # stream rows + transmissivity
        if len(self.levels) > 0:
            return len(self.levels) + 1
        else:
            return 0

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
        if len(self.levels) > 0:
            return len(self.levels[0])
        return 0

    def setData(
        self,
        index: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex,
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

            # try converting string to number
            try:
                value = float(value)
            except (TypeError, ValueError):
                value = None

            # transmissivity
            if index.row() == self.rowCount() - 1:
                self.transmissivity[index.column()] = value
            # level
            else:
                self.levels[index.row()][index.column()] = value

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
        return (
            Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
        )
