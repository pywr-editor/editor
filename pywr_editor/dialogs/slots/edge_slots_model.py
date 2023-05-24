from typing import Any, Callable

import PySide6
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QMessageBox

from pywr_editor.model import Edges


class EdgeSlotsModel(QAbstractTableModel):
    def __init__(
        self,
        edges_obj: Edges,
        callback: Callable[[str, str, int, str | int | None, bool], None],
    ):
        """
        Initialises the model.
        :param edges_obj: The Edges instance.
        """
        super().__init__()
        self.edges = edges_obj.get_all()
        self.edges_obj = edges_obj
        self.model = self.edges_obj.model
        self.callback = callback

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
            if index.isValid() is False:
                return

            # source and target nodes are always provided
            if index.column() in [0, 1]:
                return self.edges[index.row()][index.column()]
            else:
                # the slot may not be provided
                try:
                    value = self.edges[index.row()][index.column()]
                    if value is None:
                        return ""
                    # force to string to use QLinEdit
                    return str(value)
                except IndexError:
                    return ""

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
        labels = ["Source", "Target", "Slot from", "Slot to"]
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return labels[section]

    def rowCount(
        self,
        parent: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex = ...,
    ) -> int:
        """
        Provides the total number of rows.
        :param parent: The parent.
        :return: The row count.
        """
        return len(self.edges)

    def columnCount(
        self,
        parent: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex = ...,
    ) -> int:
        """
        Provides the total number of columns.
        :param parent: The parent.
        :return: The column count.
        """
        return 4

    def setData(
        self,
        index: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex,
        value: Any,
        role: int = ...,
    ) -> bool:
        """
        Updates the data.
        :param index: The table index being changed.
        :param value: The new value.
        :param role: The role.
        :return: True on success, False otherwise.
        """
        if role == Qt.ItemDataRole.EditRole:
            if not self.checkIndex(index):
                return False

            # QLineEdit return an empty string
            if value == "":
                value = None
            else:
                # try converting value to int, otherwise use str
                try:
                    value = int(value)
                except ValueError:
                    pass

            # check the type of source node being changed
            edge_names = self.edges[index.row()][0:2]
            node_dict = self.model.nodes.config(edge_names[0], as_dict=False)
            types_to_check = self.model.pywr_node_data.get_keys_with_parent_class(
                "MultiSplitLink"
            ) + self.model.includes.get_keys_with_subclass("MultiSplitLink", "node")

            if node_dict.key in types_to_check and value is None:
                QMessageBox().critical(
                    self.parent(),
                    "Cannot update the slot",
                    f"The slot name for the '{edge_names[0]}' node is mandatory",
                )
                return False

            # update the model
            self.callback(
                edge_names[0],
                edge_names[1],
                index.column() - 1,
                value,
                node_dict.key in types_to_check,
            )
            # noinspection PyUnresolvedReferences
            self.dataChanged.emit(index.row(), index.column())

            return True

        return False

    def flags(
        self,
        index: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex,
    ) -> PySide6.QtCore.Qt.ItemFlag:
        """
        Handles the item flags to make only the slot cells editable.
        :param index: The item index.
        :return: The item flags.
        """
        if index.column() in [0, 1]:
            return Qt.ItemFlag.ItemIsSelectable
        else:
            return (
                Qt.ItemFlag.ItemIsEditable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
            )
