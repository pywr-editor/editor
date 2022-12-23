from typing import TYPE_CHECKING

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

        self.empty_page = ScenarioEmptyPageWidget()
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
