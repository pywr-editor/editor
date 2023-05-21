from typing import Any

import PySide6
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import QIcon, Qt

from pywr_editor.model import ModelConfig
from pywr_editor.widgets import ExtensionIcon


class TablesListModel(QAbstractTableModel):
    def __init__(self, table_names: list[str], model_config: ModelConfig):
        """
        Initialises the model.
        :param table_names: The list of table names.
        :param model_config: The ModelConfig instance.
        """
        super().__init__()
        self.model_config = model_config
        self.table_names = table_names
        # provide alphabetical list like in components tree
        self.table_names.sort()

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
        table_name = self.table_names[index.row()]
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return table_name
        elif (
            role == Qt.ItemDataRole.DecorationRole
            or role == Qt.ItemDataRole.ToolTipRole
        ):
            ext = self.model_config.tables.get_table_extension(table_name=table_name)
            if ext is None:
                ext = "csv"

            if role == Qt.ItemDataRole.ToolTipRole:
                return f"{ext.upper().replace('.', '')} table"
            return QIcon(ExtensionIcon(ext))

    def rowCount(
        self,
        parent: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex = ...,
    ) -> int:
        """
        Provides the total number of rows.
        :param parent: The parent.
        :return: The row count.
        """
        return len(self.table_names)

    def columnCount(
        self,
        parent: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex = ...,
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
        index: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex,
    ) -> PySide6.QtCore.Qt.ItemFlag:
        """
        Handles the item flags to make each cell editable.
        :param index: The item index.
        :return: The item flags.
        """
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
