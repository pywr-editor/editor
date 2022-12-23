from typing import Union

import PySide6
from PySide6.QtCore import (
    QAbstractTableModel,
    QItemSelectionModel,
    QModelIndex,
    Slot,
)
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QPushButton, QTableView, QWidget

from pywr_editor.style import Color, stylesheet_dict_to_str

from .list_view import ListView


class TableView(QTableView):
    def __init__(
        self,
        model: QAbstractTableModel,
        toggle_buttons_on_selection: Union[
            QPushButton, list[QPushButton], None
        ] = None,
        parent: QWidget = None,
    ):
        """
        Initialises the TableView.
        :param model: The model.
        :param toggle_buttons_on_selection: The buttons to enable when at least one
        table item is selected, or to disable when no item is selected. Default to
        None. When available, the button is disabled if no table item is selected
        when the dataChanged or layoutChanged Slots are emitted.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        # action buttons
        self.toggle_buttons_on_selection = toggle_buttons_on_selection
        if toggle_buttons_on_selection is not None and not isinstance(
            toggle_buttons_on_selection, list
        ):
            self.toggle_buttons_on_selection = [toggle_buttons_on_selection]

        self.parent = parent
        self.model = model

        # style
        self.setSortingEnabled(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.horizontalHeader().setHighlightSections(False)

        self.verticalHeader().hide()
        self.setAlternatingRowColors(False)
        self.setStyleSheet(self.stylesheet())
        self.verticalScrollBar().setContextMenuPolicy(
            Qt.ContextMenuPolicy.NoContextMenu
        )

        self.setModel(model)

        # disable buttons when there are no items
        if self.toggle_buttons_on_selection is not None:
            # noinspection PyUnresolvedReferences
            self.model.layoutChanged.connect(self.on_empty_table)
            # noinspection PyUnresolvedReferences
            self.model.dataChanged.connect(self.on_selection_change)
            # noinspection PyUnresolvedReferences
            self.model.layoutChanged.connect(self.on_selection_change)

    def selectionChanged(
        self,
        selected: PySide6.QtCore.QItemSelection,
        deselected: PySide6.QtCore.QItemSelection,
    ) -> None:
        """
        Enables/disables the buttons linked to the table when at least one item is
        selected.
        :param selected: The selected items.
        :param deselected: The deselected items.
        :return: None
        """
        if self.toggle_buttons_on_selection is not None:
            [
                button.setDisabled(selected.size() == 0)
                for button in self.toggle_buttons_on_selection
            ]
        super().selectionChanged(selected, deselected)

    @Slot()
    def on_empty_table(self) -> None:
        """
        Disables the buttons when there are no items in the model.
        :return: None
        """
        if self.toggle_buttons_on_selection is not None:
            [
                button.setDisabled(self.model.rowCount() == 0)
                for button in self.toggle_buttons_on_selection
            ]

    @Slot()
    def on_selection_change(self) -> None:
        """
        Disables the buttons when the selection changes in the model.
        :return: None
        """
        selection = self.selectionModel().selection()
        [
            button.setDisabled(True if selection.indexes() else False)
            for button in self.toggle_buttons_on_selection
        ]

    def find_index_by_name(
        self, name: str, column: int = 0
    ) -> QModelIndex | None:
        """
        Finds the model index in the model data matching name.
        :param name: The name to look for.
        :param column: The column where to look for the name. Default to 0.
        :return: The model index if found, None otherwise.
        """
        all_indexes = [
            self.model.index(i, column) for i in range(self.model.rowCount())
        ]
        all_data = [index.data() for index in all_indexes]
        try:
            idx = all_data.index(name)
            return all_indexes[idx]
        except ValueError:
            return None

    def select_row_by_name(self, name: str, column: int = 0) -> None:
        """
        Selects a table row by looking for name in the model data in a column.
        :param name: The name to look for.
        :param column: The column where to look for the name. Default to 0.
        :return: None
        """
        index = self.find_index_by_name(name, column)
        if index is not None:
            self.selectionModel().select(index, QItemSelectionModel.Select)
            self.scrollTo(index, QTableView.ScrollHint.PositionAtCenter)

    def clear_selection(self) -> None:
        """
        Clear the current selection and restore the focus on the widget. This method
        can be called when the current selection changes (for example when an item is
        deleted from the model).
        :return: None
        """
        self.clearSelection()
        self.setFocus()

    @staticmethod
    def stylesheet(as_string: bool = True) -> str | dict:
        """
        Defines the widget stylesheet.
        :param as_string: Returns the stylesheet as string if True, as dictionary
        otherwise.
        :return: The stylesheet as string.
        """
        style = ListView.stylesheet(as_string=False)
        new_style: dict = {}
        for key, value in style.items():
            if "ListView" in key:
                key = key.replace("ListView", "TableView")

            new_style[key] = value

        # remove border radius on cell
        new_style["TableView"]["::item"]["border-radius"] = "0px"
        # style section
        new_style["QHeaderView::section"] = {
            "background": Color("neutral", 100).hex,
            "height": "20px",
            "padding-top": "4px",
            "padding-left": "6px",
            "font-size": "110%",
            "border": f"1px solid {Color('neutral', 300).hex}",
        }

        if as_string:
            return stylesheet_dict_to_str(new_style)
        return new_style
