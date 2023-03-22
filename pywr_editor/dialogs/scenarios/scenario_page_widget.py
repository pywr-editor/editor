from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig
from pywr_editor.utils import maybe_delete_component
from pywr_editor.widgets import PushButton

from .scenario_form_widget import ScenarioFormWidget

if TYPE_CHECKING:
    from .scenario_pages_widget import ScenarioPagesWidget


class ScenarioPageWidget(QWidget):
    def __init__(
        self,
        name: str,
        model_config: ModelConfig,
        parent: "ScenarioPagesWidget",
    ):
        """
        Initialises the widget with the form to edit a scenario.
        :param name: The scenario name.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.name = name
        self.pages = parent
        self.model_config = model_config
        self.scenario_dict = model_config.scenarios.get_config_from_name(name)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # form title
        self.title = FormTitle()
        self.set_page_title(name)

        # buttons
        close_button = PushButton("Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(parent.dialog.reject)

        # noinspection PyTypeChecker
        save_button = PushButton("Save scenario")
        save_button.setObjectName("save_button")

        add_button = PushButton("Add new scenario")
        add_button.setObjectName("add_button")
        # noinspection PyUnresolvedReferences
        add_button.clicked.connect(parent.on_add_new_scenario)

        delete_button = PushButton("Delete scenario")
        # noinspection PyUnresolvedReferences
        delete_button.clicked.connect(self.on_delete_scenario)

        button_box = QHBoxLayout()
        button_box.addWidget(save_button)
        button_box.addWidget(delete_button)
        button_box.addStretch()
        button_box.addWidget(add_button)
        button_box.addWidget(close_button)

        # form
        self.form = ScenarioFormWidget(
            name=name,
            model_config=model_config,
            scenario_dict=self.scenario_dict,
            save_button=save_button,
            parent=self,
        )

        layout.addWidget(self.title)
        layout.addWidget(self.form)
        layout.addLayout(button_box)

    def set_page_title(self, scenario_name: str) -> None:
        """
        Sets the page title.
        :param scenario_name: The scenario name.
        :return: None
        """
        self.title.setText(f"Scenario: {scenario_name}")

    @Slot()
    def on_delete_scenario(self) -> None:
        """
        Deletes the selected scenario.
        :return: None
        """
        dialog = self.pages.dialog
        list_widget = dialog.scenarios_list_widget.list
        list_model = list_widget.model

        # check if scenario is being used and warn before deleting
        total_components = self.model_config.scenarios.is_used(self.name)

        # ask before deleting
        if maybe_delete_component(self.name, total_components, self):
            # remove the scenario from the model
            # noinspection PyUnresolvedReferences
            list_model.layoutAboutToBeChanged.emit()
            list_model.scenario_names.remove(self.name)
            # noinspection PyUnresolvedReferences
            list_model.layoutChanged.emit()
            list_widget.clear_selection()

            # remove the page widget
            page_widget = self.pages.pages[self.name]
            page_widget.deleteLater()
            del self.pages.pages[self.name]

            # delete the scenario from the model configuration
            self.model_config.scenarios.delete(self.name)

            # update tree and status bar
            if dialog.app is not None:
                if hasattr(dialog.app, "components_tree"):
                    dialog.app.components_tree.reload()
                if hasattr(dialog.app, "statusBar"):
                    dialog.app.statusBar().showMessage(
                        f'Deleted scenario "{self.name}"'
                    )

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        """
        Loads the form only when the page is requested.
        :param event: The event being triggered.
        :return: None
        """
        if self.form.loaded is False:
            self.form.load_fields()

        super().showEvent(event)
