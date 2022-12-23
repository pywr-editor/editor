from typing import Any

import PySide6
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt

"""
 Model used to store values for a scenario.
"""


class NodesAndFactorsModel(QAbstractTableModel):
    def __init__(
        self,
        values: dict[str, list[str] | list[float] | None],
    ):
        """
        Initialises the model.
        :param values: A dictionary with the list of nodes and factors.
        """
        super().__init__()

        if values is not None:
            self.nodes: list[str] = values["nodes"] if "nodes" in values else []
            self.factors: list[float] = (
                values["factors"] if "factors" in values else []
            )

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
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return self.nodes[index.row()]
            elif index.column() == 1:
                return self.factors[index.row()]

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
        Returns the number of columns.
        :param parent: The parent.
        :return: The column count.
        """
        return 2

    def headerData(
        self,
        section: int,
        orientation: PySide6.QtCore.Qt.Orientation,
        role: int = ...,
    ) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if section == 0:
                return "Node"
            elif section == 1:
                return "Factor"
