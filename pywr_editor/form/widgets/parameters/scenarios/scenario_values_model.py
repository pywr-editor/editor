from typing import Any

import PySide6
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt

"""
 Model used to store values for a scenario.
"""


class ScenarioValuesModel(QAbstractTableModel):
    def __init__(
        self,
        values: list[list[int | float]] | None = None,
    ):
        """
        Initialises the model.
        :param values: The list of values.
        """
        super().__init__()

        self.values = values
        if self.values is None:
            self.values = []

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
        if role == Qt.ItemDataRole.DisplayRole:
            return f"Ensemble {index.row() + 1}"
        elif role == Qt.ItemDataRole.ToolTipRole:
            value = list(map(str, self.values[index.row()]))
            return ", ".join(value)

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
        return 1
