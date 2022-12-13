from typing import Any

import PySide6
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt


class MetadataCustomFieldsModel(QAbstractTableModel):
    def __init__(self, fields: list[list[str, Any]] | None = None):
        """
        Initialises the model.
        :param fields: The list of custom fields. This contains a list of strings whose
        first element is the field key and last item is the field value.
        """
        super().__init__()
        self.fields = fields

        if self.fields is None:
            self.fields = []

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
            return self.fields[index.row()][index.column()]

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
                return "Name"
            elif section == 1:
                return "Value"

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
        return len(self.fields)

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
            # field cannot be left empty
            if len(value.strip()) == 0:
                return False
            # key cannot be duplicated
            self.fields[index.row()][index.column()] = value
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
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsEnabled
        )
