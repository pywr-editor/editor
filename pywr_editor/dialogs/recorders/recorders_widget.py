from typing import TYPE_CHECKING

from PySide6.QtCore import QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from pywr_editor.model import ModelConfig

from .recorders_list_model import RecordersListModel
from .recorders_list_widget import RecordersListWidget

if TYPE_CHECKING:
    from .recorders_dialog import RecordersDialog


class RecordersWidget(QWidget):
    def __init__(self, model_config: ModelConfig, parent: "RecordersDialog"):
        """
        Initialises the widget showing the list of available recorders.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.model_config = model_config
        self.dialog = parent
        self.app = self.dialog.app

        # Model
        self.model = RecordersListModel(
            recorder_names=list(self.model_config.recorders.names),
            model_config=model_config,
        )

        # Recorders list
        # sort components by name
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.list = RecordersListWidget(
            model=self.model,
            proxy_model=self.proxy_model,
            parent=self,
        )
        self.list.setModel(self.proxy_model)
        self.list.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # Global layout
        layout = QVBoxLayout()
        layout.addWidget(self.list)

        # Style
        self.setLayout(layout)
        self.setMaximumWidth(260)
