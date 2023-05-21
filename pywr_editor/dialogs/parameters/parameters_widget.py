from typing import TYPE_CHECKING

from PySide6.QtCore import QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from pywr_editor.model import ModelConfig

from .parameters_list_model import ParametersListModel
from .parameters_list_widget import ParametersListWidget

if TYPE_CHECKING:
    from .parameters_dialog import ParametersDialog


class ParametersWidget(QWidget):
    def __init__(self, model_config: ModelConfig, parent: "ParametersDialog"):
        """
        Initialises the widget showing the list of available parameters.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.model_config = model_config
        self.dialog = parent
        self.app = self.dialog.app

        # Model
        self.model = ParametersListModel(
            parameter_names=list(self.model_config.parameters.names),
            model_config=model_config,
        )

        # Parameters list
        # sort components by name
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.list = ParametersListWidget(
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
