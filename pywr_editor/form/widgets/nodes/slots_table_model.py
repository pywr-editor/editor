from typing import Any

import PySide6
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt


class SlotsTableModel(QAbstractTableModel):
    def __init__(
        self,
        slot_map,
        factor_map,
    ):
        """
        Initialises the model.
        :param slot_map: A dictionary containing the node names as keys and the slot
        names as values.
        :param factor_map: A dictionary containing the node names as keys and the
        factors as values.
        """
        super().__init__()
        if len(slot_map) != len(factor_map):
            raise ValueError(
                "The length of slot_map must match the length of factor_map"
            )
        if slot_map.keys() != factor_map.keys():
            raise ValueError(
                "The keys in slot_map must match the keys in factor_map"
            )

        self.header = ["Slot name", "Factors"]
        self.nodes = list(slot_map.keys())
        self.slot_names = list(slot_map.values())
        self.factors = list(factor_map.values())

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
        if index.isValid() is False or role not in [
            Qt.ItemDataRole.DisplayRole,
            Qt.ItemDataRole.EditRole,
        ]:
            return

        # slot names
        if index.column() == 0:
            value = self.slot_names[index.row()]
            if value is None:
                return ""
            else:
                return str(value).strip()
        # factors
        if index.column() == 1:
            value = self.factors[index.row()]
            if value is None:
                return ""
            else:
                return str(value).strip()

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
        if role != Qt.ItemDataRole.DisplayRole:
            return

        if orientation == Qt.Orientation.Horizontal:
            return self.header[section]
        else:
            return self.nodes[section]

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
        return len(self.nodes)

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
        return 2

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

            row = index.row()

            # slot names
            if index.column() == 0:
                if value.strip() == "":
                    self.slot_names[row] = None
                    # noinspection PyUnresolvedReferences
                    self.dataChanged.emit(index.row(), index.column())
                    return True

                # try converting value to int, otherwise use str
                try:
                    value = int(value)
                except ValueError:
                    pass
                self.slot_names[row] = value
            # factors
            elif index.column() == 1:
                if value.strip() == "":
                    self.factors[row] = None
                    # noinspection PyUnresolvedReferences
                    self.dataChanged.emit(index.row(), index.column())

                # convert to number
                try:
                    self.factors[row] = float(value)
                except ValueError:
                    self.factors[row] = None

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
        Handles the item flags.
        :param index: The item index.
        :return: The item flags.
        """
        return (
            Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
        )
