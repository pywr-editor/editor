from typing import TYPE_CHECKING, Union

from PySide6.QtCore import QSortFilterProxyModel, Qt, QUuid, Slot
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QDialog, QHBoxLayout

from pywr_editor.model import ModelConfig

from ..base.component_dialog_splitter import ComponentDialogSplitter
from ..base.component_list import ComponentList
from ..base.component_pages import ComponentPages
from .scenario_empty_page import ScenarioEmptyPage
from .scenario_page import ScenarioPage
from .scenarios_list_model import ScenariosListModel

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class ScenariosDialog(QDialog):
    def __init__(
        self,
        model: ModelConfig,
        selected_name: str | None = None,
        parent: Union[QWindow, "MainWindow", None] = None,
    ):
        """
        Initialise the modal dialog to handle scenarios.
        :param model: The ModelConfig instance.
        :param selected_name: The name of the scenario to select.
        Default to None.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.app = parent
        self.model = model

        # Right widget
        self.pages = ComponentPages(self)

        # add pages
        empty_page = ScenarioEmptyPage(self.pages)
        self.pages.add_page("empty_page", empty_page, True)
        for name in model.scenarios.names:
            self.pages.add_page(name, ScenarioPage(name, model, self.pages))

        # Left widget
        # models
        self.list_model = ScenariosListModel(
            scenario_names=list(model.scenarios.names),
            model_config=model,
        )
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.list_model)
        self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        # widget
        self.list = ComponentList(self.list_model, self.proxy_model, empty_page, self)
        self.list.setMaximumWidth(290)

        # setup dialog
        self.setWindowTitle("Scenarios")
        self.setMinimumSize(1000, 750)
        splitter = ComponentDialogSplitter(self.list, self.pages, self.app)

        modal_layout = QHBoxLayout(self)
        modal_layout.setContentsMargins(0, 0, 5, 0)
        modal_layout.addWidget(splitter)

        # select a scenario
        if selected_name is not None:
            found = self.pages.set_page_by_name(selected_name)
            if found is False:
                return

            # noinspection PyTypeChecker
            page: ScenarioPage = self.pages.currentWidget()
            page.form.load_fields()
            # set the selected item in the list
            self.list.table.select_row_by_name(selected_name)

    @Slot()
    def add_scenario(self) -> None:
        """
        Adds a new scenario. This creates a new scenario in the model and adds, and
        selects the form page.
        :return: None
        """
        # generate unique name
        scenario_name = f"Scenario {QUuid().createUuid().toString()[1:7]}"

        # add the dictionary to the model
        self.model.scenarios.update(scenario_name, {})

        # add the page
        new_page = ScenarioPage(scenario_name, self.model, self.pages)
        self.pages.add_page(scenario_name, new_page)
        new_page.show()

        # add it to the list model
        self.list_model.layoutAboutToBeChanged.emit()
        self.list_model.scenario_names.append(scenario_name)
        self.list_model.layoutChanged.emit()

        # select the item
        table = self.list.table
        new_index = self.proxy_model.mapFromSource(
            table.find_index_by_name(scenario_name)
        )
        table.setCurrentIndex(new_index)

        # update tree and status bar
        if self.app is not None:
            if hasattr(self.app, "components_tree"):
                self.app.components_tree.reload()
            if hasattr(self.app, "statusBar"):
                self.app.statusBar().showMessage(
                    f'Added new scenario "{scenario_name}"'
                )
