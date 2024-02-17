from enum import Enum
from typing import Any

import PySide6
from PySide6.QtCore import QAbstractListModel, QSize
from PySide6.QtGui import QIcon, Qt

from pywr_editor.model import ModelConfig
from pywr_editor.node_shapes import get_node_icon, get_pixmap_from_type
from pywr_editor.widgets import ExtensionIcon, ParameterIcon, RecorderIcon


class ItemType(Enum):
    NODE = 0
    """ The item type is a node """
    PARAMETER = 1
    """ The item type is a parameter """
    RECORDER = 2
    """ The item type is a recorder """
    TABLE = 3
    """ The item type is a table """


class SearchModel(QAbstractListModel):
    def __init__(self, model_config: ModelConfig):
        """
        Initialises the model.
        :param model_config: The ModelConfig instance.
        """
        super().__init__()

        self.model_config = model_config
        self.model_data = []
        for name in model_config.tables.names:
            self.model_data.append(
                {
                    "name": name,
                    "icon": QIcon(
                        ExtensionIcon(model_config.tables.get_extension(name))
                    ),
                    "comp_type": None,
                    "type": ItemType.TABLE.value,
                }
            )
        for name in model_config.parameters.names:
            param_obj = model_config.parameters.config(name, as_dict=False)
            self.model_data.append(
                {
                    "name": name,
                    "icon": QIcon(ParameterIcon(param_obj.key)),
                    "comp_type": f"{param_obj.humanised_type} - parameter",
                    "type": ItemType.PARAMETER.value,
                }
            )

        for name in model_config.recorders.names:
            recorder_obj = model_config.recorders.config(name, as_dict=False)
            self.model_data.append(
                {
                    "name": name,
                    "icon": QIcon(RecorderIcon(recorder_obj.key)),
                    "comp_type": f"{recorder_obj.humanised_type} - recorder",
                    "type": ItemType.RECORDER.value,
                }
            )

        icon_size = QSize(25, 24)
        for name in model_config.nodes.names:
            node_obj = model_config.nodes.config(name, as_dict=False)

            # Add the icon for the current node type
            icon, _ = get_pixmap_from_type(
                icon_size, get_node_icon(model_node_obj=node_obj)
            )
            self.model_data.append(
                {
                    "name": name,
                    "icon": QIcon(icon),
                    "comp_type": node_obj.humanised_type,
                    "type": ItemType.NODE.value,
                }
            )

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
        row = self.model_data[index.row()]

        if role == Qt.ItemDataRole.EditRole:
            return row["name"]
        elif role == Qt.ItemDataRole.DisplayRole:
            label = row["name"]
            if row["comp_type"]:
                label += f" ({row['comp_type']})"
            return label
        elif role == Qt.ItemDataRole.UserRole:
            return row["type"]
        elif role == Qt.ItemDataRole.DecorationRole:
            return row["icon"]

    def rowCount(
        self,
        parent: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex = ...,
    ) -> int:
        """
        Provides the total number of rows.
        :param parent: The parent.
        :return: The row count.
        """
        return len(self.model_data)

    def columnCount(
        self,
        parent: PySide6.QtCore.QModelIndex | PySide6.QtCore.QPersistentModelIndex = ...,
    ) -> int:
        """
        Provides the total number of columns.
        :param parent: The parent.
        :return: The column count.
        """
        return 1
