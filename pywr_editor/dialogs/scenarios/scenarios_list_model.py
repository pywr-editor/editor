import PySide6
from typing import Any
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt
from pywr_editor.model import ModelConfig


class ScenariosListModel(QAbstractTableModel):
    def __init__(self, scenario_names: list[str], model_config: ModelConfig):
        """
        Initialises the model.
        :param scenario_names: The list of scenario names.
        """
        super().__init__()
        self.scenario_names = scenario_names
        self.model_config = model_config

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
        scenario_name = self.scenario_names[index.row()]

        if (
            role == Qt.ItemDataRole.DisplayRole
            or role == Qt.ItemDataRole.ToolTipRole
            or role == Qt.ItemDataRole.DecorationRole
        ):
            return scenario_name

    def rowCount(
        self,
        parent=...,
    ):
        """
        Provides the total number of rows.
        :param parent: The parent.
        :return: The row count.
        """
        return len(self.scenario_names)

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
