from typing import TYPE_CHECKING, Union

from PySide6.QtGui import QWindow

from pywr_editor.model import ModelConfig
from pywr_editor.widgets import SettingsDialog

from .scenario_pages_widget import ScenarioPagesWidget
from .scenarios_widget import ScenariosWidget

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class ScenariosDialog(SettingsDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        selected_scenario_name: str | None = None,
        parent: Union[QWindow, "MainWindow", None] = None,
    ):
        """
        Initialises the modal dialog to handle scenarios.
        :param model_config: The ModelConfig instance.
        :param selected_scenario_name: The name of the scenario to select.
        Default to None.
        :param parent: The parent widget. Default to None.
        """
        self.app = parent
        super().__init__(parent)

        # pages - init before list
        self.pages = ScenarioPagesWidget(
            model_config=model_config,
            parent=self,
        )

        # scenarios list
        self.model_config = model_config
        self.scenarios_list_widget = ScenariosWidget(
            model_config=model_config,
            parent=self,
        )

        self.setup(self.scenarios_list_widget, self.pages)
        self.setWindowTitle("Model scenarios")
        self.setMinimumSize(800, 600)

        # select a scenario
        if selected_scenario_name is not None:
            # load the page and the form fields
            found = self.pages.set_current_widget_by_name(
                selected_scenario_name
            )
            # do not load the form is the parameter is not found
            if found is False:
                return
            # noinspection PyUnresolvedReferences
            self.pages.currentWidget().form.load_fields()

            # set the selected item in the list
            scenarios_list = self.scenarios_list_widget.list
            scenarios_list.select_row_by_name(selected_scenario_name)
