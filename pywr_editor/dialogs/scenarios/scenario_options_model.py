import PySide6
from typing import Any
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtGui import Qt


class ScenarioOptionsModel(QAbstractTableModel):
    def __init__(self, slice_idx: list[int], names: list[str], total_rows: int):
        """
        Initialises the model.
        :param slice_idx: The slice.
        :param names: The ensemble_names. This must have the same size as the scenario,
        if the list is not empty.
        :param total_rows: The scenario size.
        """
        super().__init__()

        self.slice = slice_idx
        # if slice is empty, enable all ensembles
        if not self.slice:
            self.slice = list(range(total_rows))

        self.names = names
        self.total_rows = total_rows

        # name list must match the scenario size
        if len(self.names) != self.total_rows:
            raise ValueError(
                f"The list of names (size {len(self.names)}) must have the same size "
                + f"of the scenario (size ({self.total_rows})"
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
        if not index.isValid():
            return None

        # checkbox column
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 2:
            # is index is in slice list, enable checkbox
            if index.row() in self.slice:
                return Qt.CheckState.Checked
            else:
                return Qt.CheckState.Unchecked
        # other columns
        elif role in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]:
            if index.column() == 0:
                return index.row() + 1
            # names list may be empty
            elif index.column() == 1:
                try:
                    return self.names[index.row()]
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
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            if section == 0:
                return "#"
            elif section == 1:
                return "Ensemble name"
            elif section == 2:
                return "Include in run"

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
        return self.total_rows

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

    def setData(
        self,
        index: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex,
        value: Any,
        role: int = ...,
    ) -> bool:
        """
        Updates the data
        :param index: The table index being changed.
        :param value: The new value.
        :param role: The role.
        :return: True on success, False otherwise.
        """
        if not index.isValid():
            return False

        # toggle the checkbox
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 2:
            # add new value when True
            if (
                Qt.CheckState(value) == Qt.CheckState.Checked
                and index.row() not in self.slice
            ):
                self.slice.append(index.row())
            # remove value
            elif (
                Qt.CheckState(value) == Qt.CheckState.Unchecked
                and index.row() in self.slice
            ):
                self.slice.remove(index.row())
            else:
                return False

            # noinspection PyUnresolvedReferences
            self.dataChanged.emit(index.row(), index.column())
            return True

        # change ensemble names
        if role == Qt.ItemDataRole.EditRole and index.column() == 1:
            self.names[index.row()] = value
            # noinspection PyUnresolvedReferences
            self.dataChanged.emit(index.row(), index.column())
            return True

        return False

    def flags(
        self,
        index: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex,
    ) -> PySide6.QtCore.Qt.ItemFlag:
        """
        Handles the item flags to make some cells editable.
        :param index: The item index.
        :return: The item flags.
        """
        # prevent change of labels
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled
        elif index.column() == 2:
            return Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
        else:
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled
