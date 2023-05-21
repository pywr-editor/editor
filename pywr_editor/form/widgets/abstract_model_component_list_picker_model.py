from typing import Any, Literal

import PySide6
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import QIcon, Qt

from pywr_editor.model import ModelConfig, ParameterConfig, RecorderConfig
from pywr_editor.utils import ModelComponentTooltip
from pywr_editor.widgets import ParameterIcon, RecorderIcon

"""
 Model used to store model components (parameters or recorders)
 configurations.
"""


class AbstractModelComponentListPickerModel(QAbstractTableModel):
    def __init__(
        self,
        model_config: ModelConfig,
        component_type: Literal["parameter", "recorder"],
        show_row_numbers: bool,
        row_number_label: str | None,
        values: list[dict | str] | None = None,
    ):
        """
        Initialises the model.
        :param model_config: The ModelConfig instance.
        :param component_type: The component type (parameter or recorder).
        :param show_row_numbers: Shows the number of the row in the table.
        :param row_number_label: The column label for the row numbers.
        :param values: The list of values.
        """
        super().__init__()

        self.component_type = component_type
        if self.is_parameter:
            self.pywr_component_data = model_config.pywr_parameter_data
        elif self.is_recorder:
            self.pywr_component_data = model_config.pywr_recorder_data
        self.total_values = len(values)
        self.model_config = model_config
        self.values = values
        if self.values is None:
            self.values = []
        self.show_row_numbers = show_row_numbers
        self.row_number_label = row_number_label

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

        if (
            role == Qt.ItemDataRole.DisplayRole
            and self.show_row_numbers
            and index.column() == 0
        ):
            return index.row() + 1

        if role in [
            Qt.ItemDataRole.DisplayRole,
            Qt.ItemDataRole.DecorationRole,
            Qt.ItemDataRole.ToolTipRole,
        ] and (
            (not self.show_row_numbers and index.column() == 0)
            or (self.show_row_numbers and index.column() == 1)
        ):
            value = self.values[index.row()]
            exists = True
            icon_class = None
            # get icon
            if self.is_parameter:
                icon_class = ParameterIcon
            elif self.is_recorder:
                icon_class = RecorderIcon

            # value is a component dictionary
            if isinstance(value, dict):
                comp_obj = None
                if self.is_parameter:
                    comp_obj = ParameterConfig(props=value)
                elif self.is_recorder:
                    comp_obj = RecorderConfig(props=value)

                name = comp_obj.humanised_type
            # value is a model component
            elif isinstance(value, str):
                exist_method = None
                config_method = None
                if self.is_parameter:
                    config_method = self.model_config.parameters
                    exist_method = config_method.exists
                elif self.is_recorder:
                    config_method = self.model_config.recorders
                    exist_method = config_method.exists

                if not exist_method(value):
                    name = value
                    exists = False
                    comp_obj = None
                else:
                    comp_obj = getattr(config_method, "config")(value, as_dict=False)
                    name = f"{comp_obj.name} ({comp_obj.humanised_type})"
            else:
                return

            if role == Qt.ItemDataRole.DisplayRole:
                return name
            elif role == Qt.ItemDataRole.DecorationRole and exists:
                return QIcon(icon_class(comp_obj.key))
            elif role == Qt.ItemDataRole.ToolTipRole:
                if exists:
                    tooltip = ModelComponentTooltip(
                        model_config=self.model_config, comp_obj=comp_obj
                    )
                    return tooltip.render()
                else:
                    return f"The model {self.component_type} does not exist"

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
            if section == 0 and self.show_row_numbers:
                return self.row_number_label

            return "Value"

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
        """
        Provides the total number of columns.
        :param parent: The parent.
        :return: The column count.
        """
        if self.show_row_numbers:
            return 2

        return 1

    @property
    def is_parameter(self) -> bool:
        """
        Returns True if the component type is a parameter.
        :return: True if the type is a parameter, False otherwise
        """
        return self.component_type == "parameter"

    @property
    def is_recorder(self) -> bool:
        """
        Returns True if the component type is a recorder.
        :return: True if the type is a recorder, False otherwise
        """
        return self.component_type == "recorder"
