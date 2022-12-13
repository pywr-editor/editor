import PySide6
from typing import Any
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt


class TablesListModel(QAbstractTableModel):
    def __init__(self, table_names: list[str]):
        """
        Initialises the model.
        :param table_names: The list of table names.
        """
        super().__init__()
        self.table_names = table_names
        # provide alphabetical list like in components tree
        self.table_names.sort()

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
            or role == Qt.ItemDataRole.ToolTipRole
        ):
            text = self.table_names[index.row()]
            return text

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
        return len(self.table_names)

    def columnCount(
        self,
        parent: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex = ...,
    ) -> int:
        ...
        """
        Provides the total number of columns.
        :param parent: The parent.
        :return: The column count.
        """
        return 1

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
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
