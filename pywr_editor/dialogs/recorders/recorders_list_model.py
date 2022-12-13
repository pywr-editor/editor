import PySide6
from typing import Any
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt, QIcon
from pywr_editor.widgets import RecorderIcon
from pywr_editor.model import ModelConfig


class RecordersListModel(QAbstractTableModel):
    def __init__(self, recorder_names: list[str], model_config: ModelConfig):
        """
        Initialises the model.
        :param recorder_names: The list of recorder names.
        """
        super().__init__()
        self.recorder_names = recorder_names
        self.model_config = model_config
        self.recorders_data = model_config.pywr_recorder_data

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
        recorder_name = self.recorder_names[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return recorder_name
        elif (
            role == Qt.ItemDataRole.ToolTipRole
            or role == Qt.ItemDataRole.DecorationRole
        ):
            recorder_config = self.model_config.recorders.get_config_from_name(
                recorder_name=recorder_name
            )

            # new recorder
            if recorder_config is None:
                if role == Qt.ItemDataRole.ToolTipRole:
                    return recorder_name
            else:
                recorder_obj = self.model_config.recorders.recorder(
                    config=recorder_config, deepcopy=True, name=recorder_name
                )
                if role == Qt.ItemDataRole.ToolTipRole:
                    pywr_recorder_name = self.recorders_data.name(
                        recorder_obj.key
                    )
                    if pywr_recorder_name is not None:
                        return (
                            f"{recorder_name} ("
                            + f"{self.recorders_data.name(recorder_obj.key)})"
                        )
                    else:
                        return f"{recorder_name} (Custom recorder)"
                else:
                    key = recorder_obj.key
                    if key is None:
                        key = "Custom recorders"
                    return QIcon(RecorderIcon(key))

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
        return len(self.recorder_names)

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
