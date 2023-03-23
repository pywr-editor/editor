from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QAbstractItemView

from pywr_editor.widgets import TableView

from .tables_list_model import TablesListModel

if TYPE_CHECKING:
    from .tables_widget import TablesWidget


class TablesListWidget(TableView):
    def __init__(
        self,
        model: TablesListModel,
        proxy_model: QSortFilterProxyModel,
        parent: "TablesWidget",
    ):
        """
        Initialises the widget showing the list of the model tables and buttons to add
        or remove tables.
        :param model: The model.
        :param proxy_model: The model to use as proxy for sorting the data.
        :param parent: The parent widget.
        """
        super().__init__(model=model, proxy_model=proxy_model, parent=parent)
        self.model = model
        self.parent = parent

        self.horizontalHeader().hide()
        self.setMaximumWidth(200)
        self.verticalHeader().setDefaultSectionSize(24)
        self.setShowGrid(False)
        self.setIconSize(QSize(21, 18))
        self.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectItems
        )
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def selectionChanged(
        self,
        selected: PySide6.QtCore.QItemSelection,
        deselected: PySide6.QtCore.QItemSelection,
    ) -> None:
        """
        When no table is selected, show the empty page.
        :param selected: The selection instance.
        :param deselected: The instance of deselected items.
        :return: None
        """
        pages_widget = self.parent.dialog.pages_widget
        if len(selected.indexes()) == 0:
            pages_widget.set_empty_page()
        else:
            table_name = selected.indexes()[0].data(Qt.ItemDataRole.DisplayRole)
            pages_widget.set_current_widget_by_name(table_name)
        super().selectionChanged(selected, deselected)
