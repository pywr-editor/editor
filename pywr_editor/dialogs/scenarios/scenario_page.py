from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig
from pywr_editor.utils import maybe_delete_component
from pywr_editor.widgets import PushIconButton

from .scenario_form_widget import ScenarioFormWidget
from .scenarios_list_model import ScenariosListModel

if TYPE_CHECKING:
    from ..base.component_pages import ComponentPages
    from .scenarios_dialog import ScenariosDialog


class ScenarioPage(QWidget):
    def __init__(
        self,
        name: str,
        model: ModelConfig,
        pages: "ComponentPages",
    ):
        """
        Initialise the widget with the form to edit a scenario.
        :param name: The scenario name.
        :param model: The ModelConfig instance.
        :param pages: The parent widget containing the stacked pages.
        """
        super().__init__(pages)
        self.name = name
        self.pages = pages

        # noinspection PyTypeChecker
        self.dialog: "ScenariosDialog" = pages.dialog
        self.model = model
        self.scenario_dict = model.scenarios.config(name)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # form title
        self.title = FormTitle()
        self.set_page_title(name)

        # buttons
        close_button = PushIconButton(icon="msc.close", label="Close")
        close_button.clicked.connect(self.dialog.reject)

        # noinspection PyTypeChecker
        save_button = PushIconButton(icon="msc.save", label="Save", accent=True)
        save_button.setObjectName("save_button")
        save_button.clicked.connect(self.on_save_scenario)

        add_button = PushIconButton(icon="msc.add", label="Add new")
        add_button.setObjectName("add_button")
        add_button.clicked.connect(self.on_add_new_scenario)

        delete_button = PushIconButton(icon="msc.remove", label="Delete")
        delete_button.setObjectName("delete_button")
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
            model=model,
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
    def on_add_new_scenario(self) -> None:
        """
        Slot called when user clicks on the "Add" button to insert a new scenario.
        :return: None
        """
        self.dialog.add_scenario()

    @Slot()
    def on_save_scenario(self) -> None:
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
            self.model.scenarios.rename(self.name, new_name)

            # update the page name in the list
            self.pages.rename_page(self.name, new_name)

            # update the page title
            self.set_page_title(new_name)

            # update the scenario list
            scenarios_model: ScenariosListModel = self.dialog.list_model
            idx = scenarios_model.scenario_names.index(self.name)
            scenarios_model.layoutAboutToBeChanged.emit()
            scenarios_model.scenario_names[idx] = new_name
            scenarios_model.layoutChanged.emit()

            self.name = new_name

        # move dictionary items from "options" field to form_data
        for key, value in form_data["options"].items():
            if value:
                form_data[key] = value
        del form_data["options"]

        # update the model with the new dictionary
        self.model.scenarios.update(self.name, form_data)

        # update the parameter list in case the name changed
        self.dialog.list.update()

        # update tree and status bar
        if self.dialog.app is not None:
            if hasattr(self.dialog.app, "components_tree"):
                self.dialog.app.components_tree.reload()
            if hasattr(self.dialog.app, "statusBar"):
                self.dialog.app.statusBar().showMessage(
                    f'Scenario "{self.name}" updated'
                )

    @Slot()
    def on_delete_scenario(self) -> None:
        """
        Delete the selected scenario.
        :return: None
        """
        # check if scenario is being used and warn before deleting
        total_components = self.model.scenarios.is_used(self.name)

        # ask before deleting
        if maybe_delete_component(self.name, total_components, self):
            # remove the scenario from the model
            self.dialog.list_model.layoutAboutToBeChanged.emit()
            self.dialog.list_model.scenario_names.remove(self.name)
            self.dialog.list_model.layoutChanged.emit()
            self.dialog.list.table.clear_selection()

            # remove the page widget
            # noinspection PyTypeChecker
            page: ScenarioPage = self.pages.findChild(ScenarioPage, self.name)
            page.deleteLater()
            # delete the scenario from the model configuration
            self.model.scenarios.delete(self.name)
            # set default page
            self.pages.set_page_by_name("empty_page")

            # update tree and status bar
            if self.dialog.app is not None:
                if hasattr(self.dialog.app, "components_tree"):
                    self.dialog.app.components_tree.reload()
                if hasattr(self.dialog.app, "statusBar"):
                    self.dialog.app.statusBar().showMessage(
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
