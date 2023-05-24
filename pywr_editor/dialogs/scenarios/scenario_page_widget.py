from typing import TYPE_CHECKING

import PySide6
import qtawesome as qta
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig
from pywr_editor.utils import maybe_delete_component
from pywr_editor.widgets import PushIconButton

from .scenario_form_widget import ScenarioFormWidget
from .scenarios_list_model import ScenariosListModel

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
        self.scenario_dict = model_config.scenarios.config(name)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # form title
        self.title = FormTitle()
        self.set_page_title(name)

        # buttons
        close_button = PushIconButton(icon=qta.icon("msc.close"), label="Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(parent.dialog.reject)

        # noinspection PyTypeChecker
        save_button = PushIconButton(icon=qta.icon("msc.save"), label="Save")
        save_button.setObjectName("save_button")
        # noinspection PyUnresolvedReferences
        save_button.clicked.connect(self.on_save)

        add_button = PushIconButton(icon=qta.icon("msc.add"), label="Add new")
        add_button.setObjectName("add_button")
        # noinspection PyUnresolvedReferences
        add_button.clicked.connect(parent.on_add_new_scenario)

        delete_button = PushIconButton(icon=qta.icon("msc.remove"), label="Delete")
        delete_button.setObjectName("delete_button")
        # noinspection PyUnresolvedReferences
        delete_button.clicked.connect(self.on_delete_scenario)

        button_box = QHBoxLayout()
        button_box.addWidget(add_button)
        button_box.addStretch()
        button_box.addWidget(save_button)
        button_box.addWidget(delete_button)
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
    def on_save(self) -> None:
        """
        Slot called when user clicks on the "Update" button. Only visible fields are
        exported.
        :return: None
        """
        form_data = self.form.save()
        if form_data is False:
            return

        new_name = form_data["name"]
        # rename scenario
        if form_data["name"] != self.name:
            # update the model configuration
            self.model_config.scenarios.rename(self.name, new_name)

            # update the page name in the list
            self.pages.rename_page(self.name, new_name)

            # update the page title
            self.set_page_title(new_name)

            # update the scenario list
            scenarios_model: ScenariosListModel = (
                self.pages.dialog.scenarios_list_widget.model
            )
            idx = scenarios_model.scenario_names.index(self.name)

            # noinspection PyUnresolvedReferences
            scenarios_model.layoutAboutToBeChanged.emit()
            scenarios_model.scenario_names[idx] = new_name
            # noinspection PyUnresolvedReferences
            scenarios_model.layoutChanged.emit()

            self.name = new_name

        # move dictionary items from "options" field to form_data
        for key, value in form_data["options"].items():
            if value:
                form_data[key] = value
        del form_data["options"]

        # update the model with the new dictionary
        self.model_config.scenarios.update(self.name, form_data)

        # update the parameter list in case the name changed
        self.pages.dialog.scenarios_list_widget.update()

        # update tree and status bar
        app = self.pages.dialog.app
        if app is not None:
            if hasattr(app, "components_tree"):
                app.components_tree.reload()
            if hasattr(app, "statusBar"):
                app.statusBar().showMessage(f'Scenario "{self.name}" updated')

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

            # set default page
            self.pages.set_empty_page()

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
        if self.form.loaded_ is False:
            self.form.load_fields()

        super().showEvent(event)
