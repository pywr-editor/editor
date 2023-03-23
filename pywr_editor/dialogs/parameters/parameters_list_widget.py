from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QAbstractItemView

from pywr_editor.widgets import TableView

from .parameters_list_model import ParametersListModel

if TYPE_CHECKING:
    from .parameters_widget import ParametersWidget


class ParametersListWidget(TableView):
    def __init__(
        self,
        model: ParametersListModel,
        proxy_model: QSortFilterProxyModel,
        parent: "ParametersWidget",
    ):
        """
        Initialises the widget showing the list of the model parameters and buttons to
        add or remove parameters.
        :param model: The model.
        :param proxy_model: The model to use as proxy for sorting the data.
        :param parent: The parent widget.
        """
        super().__init__(model=model, proxy_model=proxy_model, parent=parent)
        self.model = model
        self.parent = parent

        self.horizontalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(24)
        self.resizeColumnsToContents()

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
        When no parameter is selected, show the empty page.
        :param selected: The selection instance.
        :param deselected: The instance of deselected items.
        :return: None
        """
        pages_widget = self.parent.dialog.pages_widget
        if len(selected.indexes()) == 0:
            pages_widget.set_empty_page()
        else:
            parameter_name = selected.indexes()[0].data(
                Qt.ItemDataRole.DisplayRole
            )
            pages_widget.set_current_widget_by_name(parameter_name)
        super().selectionChanged(selected, deselected)
