import PySide6
from typing import Any
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt
from pywr_editor.model import ModelConfig


class DictionaryModel(QAbstractTableModel):
    def __init__(self, dictionary: dict[str, Any], model_config: ModelConfig):
        """
        Initialises the model.
        :param dictionary: The dictionary.
        :param model_config: The ModelConfig instance.
        """
        super().__init__()
        self.dictionary = dictionary
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
        if index.isValid() is False:
            return

        keys = list(self.dictionary.keys())
        values = list(self.dictionary.values())

        if index.column() == 0 and role == Qt.ItemDataRole.DisplayRole:
            return keys[index.row()]
        else:
            value = values[index.row()]

            data_type = "Not supported"
            data_value = str(value)
            data_tooltip = None
            if isinstance(value, bool):
                data_type = "Boolean"
            elif isinstance(value, (float, int)):
                data_type = "Number"
            elif isinstance(value, str):
                if value in self.model_config.nodes.names:
                    data_type = "Node"
                elif value in self.model_config.parameters.names:
                    data_type = "Parameter"
                elif value in self.model_config.recorders.names:
                    data_type = "Recorder"
                elif value in self.model_config.tables.names:
                    data_type = "Table"
                elif value in self.model_config.scenarios.names:
                    data_type = "Scenario"
                else:
                    data_type = "String"
            elif isinstance(value, list):
                if all([isinstance(v, (float, int)) for v in value]):
                    data_type = "1D array"
                    data_value = ", ".join(map(str, value))
                elif all([isinstance(v, list) for v in value]):
                    if len(value) == 2:
                        data_type = "2D array"
                        data_tooltip = self.array_tooltip(value)
                    elif len(value) == 3:
                        data_type = "3D array"
                        data_tooltip = self.array_tooltip(value)
                # elif all([isinstance(v, str) for v in value]):
                #     data_type = "List of strings"
                #     data_value = ", ".join(value)
            elif isinstance(value, dict):
                data_type = "Dictionary"

            # data type
            if (
                index.column() == 1
                and role == Qt.ItemDataRole.DisplayRole
                and data_type
            ):
                return data_type
            # value
            elif index.column() == 2 and data_value:
                if role == Qt.ItemDataRole.DisplayRole:
                    return data_value
                elif role == Qt.ItemDataRole.ToolTipRole:
                    return data_tooltip if data_tooltip else data_value

    @staticmethod
    def array_tooltip(value: list) -> str:
        """
        Returns the tooltip string for a multi-dimensional array.
        :param value: The list of list.
        :return: The tooltip string.
        """
        data_tooltip = [", ".join(map(str, sub_list)) for sub_list in value]
        tooltip_string = ""
        for si, string_list in enumerate(data_tooltip):
            tooltip_string += f"Dimension {si+1}: {string_list}\n"
        return tooltip_string[0:-2]

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
                return "Key"
            elif section == 1:
                return "Data type"
            else:
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
        # get the maximum length from all variables
        return len(self.dictionary)

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
        return 3

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
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
