from typing import TYPE_CHECKING

from PySide6.QtCore import QUuid, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from pywr_editor.model import ModelConfig
from pywr_editor.widgets import PushIconButton

from .scenario_pages_widget import ScenarioPagesWidget
from .scenarios_list_model import ScenariosListModel
from .scenarios_list_widget import ScenariosListWidget

if TYPE_CHECKING:
    from .scenarios_dialog import ScenariosDialog


class ScenariosWidget(QWidget):
    def __init__(self, model_config: ModelConfig, parent: "ScenariosDialog"):
        """
        Initialises the widget showing the list of available scenarios.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.model_config = model_config
        self.dialog = parent
        self.app = self.dialog.app

        # Model
        self.model = ScenariosListModel(
            scenario_names=self.model_config.scenarios.names,
            model_config=model_config,
        )
        self.add_button = PushIconButton(
            icon=":misc/plus", label="Add", parent=self
        )
        self.delete_button = PushIconButton(
            icon=":misc/minus", label="Delete", parent=self
        )

        # Scenarios list
        self.list = ScenariosListWidget(
            model=self.model, delete_button=self.delete_button, parent=self
        )

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addItem(
            QSpacerItem(10, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)

        # noinspection PyUnresolvedReferences
        self.add_button.clicked.connect(self.on_add_new_scenario)
        # noinspection PyUnresolvedReferences
        self.delete_button.clicked.connect(self.on_delete_scenario)

        # Global layout
        layout = QVBoxLayout()
        layout.addWidget(self.list)
        layout.addLayout(button_layout)

        # Style
        self.setLayout(layout)
        self.setMaximumWidth(240)

    @Slot()
    def on_delete_scenario(self) -> None:
        """
        Deletes the selected scenario.
        :return: None
        """
        # check if scenario is being used and warn before deleting
        indexes = self.list.selectedIndexes()
        if len(indexes) == 0:
            return
        scenario_name = self.model.scenario_names[indexes[0].row()]
        total_components = self.model_config.scenarios.is_used(scenario_name)

        # ask before deleting
        if self.maybe_delete(scenario_name, total_components):
            # remove the scenario from the model
            # noinspection PyUnresolvedReferences
            self.model.layoutAboutToBeChanged.emit()
            self.model.scenario_names.remove(scenario_name)
            # noinspection PyUnresolvedReferences
            self.model.layoutChanged.emit()
            self.list.clear_selection()

            # remove the page widget
            page_widget = self.dialog.pages.pages[scenario_name]
            page_widget.deleteLater()
            del self.dialog.pages.pages[scenario_name]

            # delete the scenario from the model configuration
            self.model_config.scenarios.delete(scenario_name)

            # update tree and status bar
            if self.app is not None:
                if hasattr(self.app, "components_tree"):
                    self.app.components_tree.reload()
                if hasattr(self.app, "statusBar"):
                    self.app.statusBar().showMessage(
                        f'Deleted scenario "{scenario_name}"'
                    )

    @Slot()
    def on_add_new_scenario(self) -> None:
        """
        Adds a new scenario. This creates a new scenario in the model and adds, and
        selects the form page.
        :return: None
        """
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
        self.model.layoutAboutToBeChanged.emit()
        self.model.scenario_names.append(scenario_name)
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        # select the item (this is always added as last)
        self.list.setCurrentIndex(
            self.model.index(self.model.rowCount() - 1, 0)
        )

        # update tree and status bar
        if self.app is not None:
            if hasattr(self.app, "components_tree"):
                self.app.components_tree.reload()
            if hasattr(self.app, "statusBar"):
                self.app.statusBar().showMessage(
                    f'Added new scenario "{scenario_name}"'
                )

    def maybe_delete(self, scenario_name: str, total_times: int) -> bool:
        """
        Asks user if they want to delete a scenario that's being used by a model
        component.
        :param scenario_name: The scenario name to delete.
        :param total_times: The number of times the scenario is used by the model
        components.
        :return: True whether to delete the scenario, False otherwise.
        """
        message = f"Do you want to delete {scenario_name}?"
        if total_times > 0:
            times = "time"
            if total_times > 1:
                times = f"{times}s"
            message = (
                f"The scenario '{scenario_name}' you would like to delete is used "
                + f"{total_times} {times} by the model components. If you delete it, "
                + "the model will not be able to run anymore.\n\n"
                + "Do you want to continue?"
            )
        answer = QMessageBox.warning(
            self,
            "Warning",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            return True
        elif answer == QMessageBox.StandardButton.No:
            return False
        # on discard
        return False
