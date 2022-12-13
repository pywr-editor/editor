import PySide6
from typing import TypeVar
from PySide6.QtCore import (
    QItemSelectionModel,
    Slot,
    QAbstractTableModel,
    QModelIndex,
)
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QTableView, QPushButton, QWidget
from pywr_editor.ui import Color, stylesheet_dict_to_str
from .list_view import ListView
from .push_button import PushButton
from .push_icon_button import PushIconButton

button_type = TypeVar(
    "button_type", bound=QPushButton | PushButton | PushIconButton
)


class TableView(QTableView):
    def __init__(
        self,
        model: QAbstractTableModel,
        toggle_buttons_on_selection: button_type
        | list[button_type]
        | None = None,
        parent: QWidget = None,
    ):
        """
        Initialises the TableView.
        :param model: The model.
        :param toggle_buttons_on_selection: The buttons to enable when at least one
        table item is selected, or to disable when no item is selected. Default to
        None. When available, the button is disabled if no table item is selected.
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
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.horizontalHeader().setHighlightSections(False)

        self.verticalHeader().hide()
        self.setAlternatingRowColors(False)
        self.setStyleSheet(self.stylesheet())
        self.verticalScrollBar().setContextMenuPolicy(Qt.NoContextMenu)

        self.setModel(model)

        # disable buttons when there are no items
        if self.toggle_buttons_on_selection is not None:
            # noinspection PyUnresolvedReferences
            self.model.layoutChanged.connect(self.on_layout_changed)
            # noinspection PyUnresolvedReferences
            self.model.dataChanged.connect(self.on_value_changed)
            # noinspection PyUnresolvedReferences
            self.model.layoutChanged.connect(self.on_value_changed)

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
    def on_layout_changed(self) -> None:
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
    def on_value_changed(self) -> None:
        selection = self.selectionModel().selection()

        [
            button.setDisabled(
                selection.indexes().size > 0 if selection.indexes() else False
            )
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
            self.scrollTo(index, self.PositionAtCenter)

    @staticmethod
    def stylesheet(as_string: bool = True) -> str | dict:
        """
        Defines the widget stylesheet.
        :param as_string: Returns the stylesheet as string if True, as dictionary
        otherwise.
        :return: The stylesheet as string.
        """
        style = ListView.stylesheet(as_string=False)
        for key, value in style.items():
            if "ListView" in key:
                del style[key]
                key = key.replace("ListView", "TableView")
                style[key] = value

        # remove border radius on cell
        style["TableView"]["::item"]["border-radius"] = "0px"
        # style section
        style["QHeaderView::section"] = {
            "background": Color("neutral", 100).hex,
            "height": "20px",
            "padding-top": "4px",
            "padding-left": "6px",
            "font-size": "110%",
            "border": f"1px solid {Color('neutral', 300).hex}",
            # "border-top": "1px solid transparent",
            # "border-left": "1px solid transparent",
        }

        if as_string:
            return stylesheet_dict_to_str(style)
        return style
