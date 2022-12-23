from typing import TYPE_CHECKING

import PySide6
from PySide6.QtWidgets import QAbstractItemView, QPushButton

from pywr_editor.widgets import TableView

from .tables_list_model import TablesListModel

if TYPE_CHECKING:
    from .tables_widget import TablesWidget


class TablesListWidget(TableView):
    def __init__(
        self,
        model: TablesListModel,
        delete_button: QPushButton,
        parent: "TablesWidget",
    ):
        """
        Initialises the widget showing the list of the model tables and buttons to add
        or remove tables.
        :param model: The model.
        :param delete_button: The delete button connected to the table.
        :param parent: The parent widget.
        """
        super().__init__(
            model=model,
            toggle_buttons_on_selection=delete_button,
            parent=parent,
        )
        self.model = model
        self.parent = parent

        self.horizontalHeader().hide()
        self.setMaximumWidth(200)
        self.verticalHeader().setDefaultSectionSize(24)
        self.setShowGrid(False)
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
            table_name = self.model.table_names[selected.indexes()[0].row()]
            pages_widget.set_current_widget_by_name(table_name)
        super().selectionChanged(selected, deselected)
