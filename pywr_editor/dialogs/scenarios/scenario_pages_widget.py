from typing import TYPE_CHECKING

from PySide6.QtCore import QUuid, Slot
from PySide6.QtWidgets import QStackedWidget

from pywr_editor.model import ModelConfig

from .scenario_empty_page_widget import ScenarioEmptyPageWidget
from .scenario_page_widget import ScenarioPageWidget

if TYPE_CHECKING:
    from .scenarios_dialog import ScenariosDialog


class ScenarioPagesWidget(QStackedWidget):
    def __init__(self, model_config: ModelConfig, parent: "ScenariosDialog"):
        """
        Initialises the widget containing the pages to edit the scenarios.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.model_config = model_config
        self.dialog = parent

        self.empty_page = ScenarioEmptyPageWidget(self)
        self.addWidget(self.empty_page)

        self.pages = {}
        for name in model_config.scenarios.names:
            self.add_new_page(name)

        self.set_empty_page()

    def add_new_page(self, scenario_name: str) -> None:
        """
        Adds a new page.
        :param scenario_name: The page or scenario name.
        :return: None
        """
        self.pages[scenario_name] = ScenarioPageWidget(
            name=scenario_name, model_config=self.model_config, parent=self
        )
        self.addWidget(self.pages[scenario_name])

    def rename_page(self, scenario_name: str, new_scenario_name: str) -> None:
        """
        Renames a page in the page dictionary.
        :param scenario_name: The scenario name to change.
        :param new_scenario_name: The new scenario name.
        :return: None
        """
        self.pages[new_scenario_name] = self.pages.pop(scenario_name)

    def set_empty_page(self) -> None:
        """
        Sets the empty page as visible.
        :return: None
        """
        self.setCurrentWidget(self.empty_page)

    def set_current_widget_by_name(self, scenario_name: str) -> bool:
        """
        Sets the current widget by providing the scenario name.
        :param scenario_name: The scenario name.
        :return: True if the scenario is found, False otherwise.
        """
        if scenario_name in self.pages.keys():
            self.setCurrentWidget(self.pages[scenario_name])
            return True
        return False

    @Slot()
    def on_add_new_scenario(self) -> None:
        """
        Adds a new scenario. This creates a new scenario in the model and adds, and
        selects the form page.
        :return: None
        """
        list_widget = self.dialog.scenarios_list_widget.list
        list_model = self.dialog.scenarios_list_widget.model
        proxy_model = self.dialog.scenarios_list_widget.proxy_model

        # generate unique name
        scenario_name = f"Scenario {QUuid().createUuid().toString()[1:7]}"

        # add the dictionary to the model
        self.model_config.scenarios.update(scenario_name, {})

        # add the page
        pages_widget: ScenarioPagesWidget = self.dialog.pages
        pages_widget.add_new_page(scenario_name)
        pages_widget.set_current_widget_by_name(scenario_name)

        # add it to the list model
        # noinspection PyUnresolvedReferences
        list_model.layoutAboutToBeChanged.emit()
        list_model.scenario_names.append(scenario_name)
        # noinspection PyUnresolvedReferences
        list_model.layoutChanged.emit()
        # select the item
        new_index = proxy_model.mapFromSource(
            list_widget.find_index_by_name(scenario_name)
        )
        list_widget.setCurrentIndex(new_index)

        # update tree and status bar
        if self.dialog.app is not None:
            if hasattr(self.dialog.app, "components_tree"):
                self.dialog.app.components_tree.reload()
            if hasattr(self.dialog.app, "statusBar"):
                self.dialog.app.statusBar().showMessage(
                    f'Added new scenario "{scenario_name}"'
                )
