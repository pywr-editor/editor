from typing import Any

import PySide6
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import QIcon, Qt

from pywr_editor.model import ModelConfig
from pywr_editor.widgets import ParameterIcon


class ParametersListModel(QAbstractTableModel):
    def __init__(self, parameter_names: list[str], model_config: ModelConfig):
        """
        Initialises the model.
        :param parameter_names: The list of parameter names.
        :param model_config: The ModelConfig instance.
        """
        super().__init__()
        self.parameter_names = parameter_names
        self.model_config = model_config
        self.params_data = model_config.pywr_parameter_data

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
        parameter_name = self.parameter_names[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return parameter_name
        elif (
            role == Qt.ItemDataRole.ToolTipRole
            or role == Qt.ItemDataRole.DecorationRole
        ):
            parameter_config = (
                self.model_config.parameters.get_config_from_name(
                    parameter_name
                )
            )
            # new parameter
            if parameter_config is None:
                if role == Qt.ItemDataRole.ToolTipRole:
                    return parameter_name
            else:
                parameter_obj = self.model_config.parameters.parameter(
                    config=parameter_config, deepcopy=True, name=parameter_name
                )
                if role == Qt.ItemDataRole.ToolTipRole:
                    pywr_param_name = self.params_data.name(parameter_obj.key)
                    if pywr_param_name is not None:
                        return (
                            f"{parameter_name} "
                            + f"({self.params_data.name(parameter_obj.key)})"
                        )
                    else:
                        return f"{parameter_name} (Custom parameter)"
                else:
                    key = parameter_obj.key
                    if key is None:
                        key = "Custom parameter"
                    return QIcon(ParameterIcon(key))

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
        return len(self.parameter_names)

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
