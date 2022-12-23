from typing import TYPE_CHECKING

import PySide6
from PySide6.QtWidgets import QAbstractItemView, QPushButton

from pywr_editor.widgets import TableView

from .scenarios_list_model import ScenariosListModel

if TYPE_CHECKING:
    from .scenarios_widget import ScenariosWidget


class ScenariosListWidget(TableView):
    def __init__(
        self,
        model: ScenariosListModel,
        delete_button: QPushButton,
        parent: "ScenariosWidget",
    ):
        """
        Initialises the widget showing the list of the model scenarios and buttons
        to add or remove them.
        :param model: The model.
        :param delete_button: The delete button.
        :param parent: The parent widget.
        """
        super().__init__(model, delete_button, parent)
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
        When no scenario is selected, show the empty page.
        :param selected: The selection instance.
        :param deselected: The instance of deselected items.
        :return: None
        """
        pages_widget = self.parent.dialog.pages
        if len(selected.indexes()) == 0:
            pages_widget.set_empty_page()
        else:
            scenario_name = self.model.scenario_names[
                selected.indexes()[0].row()
            ]
            pages_widget.set_current_widget_by_name(scenario_name)
        super().selectionChanged(selected, deselected)
