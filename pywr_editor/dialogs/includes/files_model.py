from pathlib import Path
from typing import Any

import PySide6
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt

from pywr_editor.model import ImportProps, ModelConfig
from pywr_editor.style import Color


class FilesModel(QAbstractTableModel):
    def __init__(
        self, files_dict: dict[Path, ImportProps], model_config: ModelConfig
    ):
        """
        Initialises the model.
        :param files_dict: A dictionary from Includes.get_custom_classes().
        """
        super().__init__()
        self.files_dict = files_dict
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
        files = list(self.files_dict.keys())

        full_file = str(files[index.row()])
        custom_classes = self.files_dict[files[index.row()]]

        if role == Qt.ItemDataRole.BackgroundRole and not custom_classes.exists:
            return Color("red", 100).qcolor

        if index.column() == 0:
            if role == Qt.ItemDataRole.DisplayRole:
                return custom_classes.name
            elif role == Qt.ItemDataRole.ToolTipRole:
                return (
                    full_file
                    if custom_classes.exists
                    else f"The file '{full_file}' does not exist"
                )
        elif index.column() == 1:
            parameters_count = len(custom_classes.parameters)
            if role == Qt.ItemDataRole.DisplayRole:
                return parameters_count
            elif role == Qt.ItemDataRole.ToolTipRole and parameters_count:
                return ", ".join(custom_classes.parameters)
        elif index.column() == 2:
            recorders_count = len(custom_classes.recorders)
            if role == Qt.ItemDataRole.DisplayRole:
                return recorders_count
            elif role == Qt.ItemDataRole.ToolTipRole and recorders_count:
                return ", ".join(custom_classes.recorders)
        elif index.column() == 3:
            nodes_count = len(custom_classes.nodes)
            if role == Qt.ItemDataRole.DisplayRole:
                return nodes_count
            elif role == Qt.ItemDataRole.ToolTipRole and nodes_count:
                return ", ".join(custom_classes.nodes)

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
        return len(self.files_dict)

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
        return 4

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
                return "File name"
            elif section == 1:
                return "Parameters"
            elif section == 2:
                return "Recorders"
            elif section == 3:
                return "Nodes"

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
