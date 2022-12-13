import PySide6
from PySide6.QtWidgets import QAbstractItemView, QPushButton
from typing import TYPE_CHECKING
from .recorders_list_model import RecordersListModel
from pywr_editor.widgets import TableView

if TYPE_CHECKING:
    from .recorders_widget import RecordersWidget


class RecordersListWidget(TableView):
    def __init__(
        self,
        model: RecordersListModel,
        delete_button: QPushButton,
        parent: "RecordersWidget",
    ):
        """
        Initialises the widget showing the list of the model recorder and buttons
        to add or remove recorders.
        :param model: The model.
        :param delete_button: The delete button connected to the recorder.
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
        When no recorder is selected, show the empty page.
        :param selected: The selection instance.
        :param deselected: The instance of deselected items.
        :return: None
        """
        pages_widget = self.parent.dialog.pages_widget
        if len(selected.indexes()) == 0:
            pages_widget.set_empty_page()
        else:
            recorder_name = self.model.recorder_names[
                selected.indexes()[0].row()
            ]
            pages_widget.set_current_widget_by_name(recorder_name)
        super().selectionChanged(selected, deselected)
