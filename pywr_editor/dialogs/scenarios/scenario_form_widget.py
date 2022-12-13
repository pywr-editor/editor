from PySide6.QtCore import Slot
from PySide6.QtWidgets import QPushButton
from typing import TYPE_CHECKING
from .scenarios_list_model import ScenariosListModel
from .scenario_options_widget import ScenarioOptionsWidget
from pywr_editor.form import ModelComponentForm, FormValidation
from pywr_editor.utils import Logging
from pywr_editor.model import ModelConfig

if TYPE_CHECKING:
    from .scenario_page_widget import ScenarioPageWidget

"""
 This forms allow editing a scenario configuration.
"""


class ScenarioFormWidget(ModelComponentForm):
    def __init__(
        self,
        name: str,
        model_config: ModelConfig,
        scenario_dict: dict,
        save_button: QPushButton,
        parent: "ScenarioPageWidget",
    ):
        """
        Initialises the scenario form.
        :param name: The scenario name.
        :param model_config: The ModelConfig instance.
        :param save_button: The button used to save the form.
        :param scenario_dict: The scenario configuration.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading with {scenario_dict}")

        self.name = name
        self.page = parent
        self.model_config = model_config
        self.scenario_dict = scenario_dict
        self.dialog = self.page.pages.dialog

        available_fields = {
            "General": [
                {
                    "name": "name",
                    "value": name,
                    "help_text": "A unique name identifying the parameter",
                    "allow_empty": False,
                    "validate_fun": self._check_scenario_name,
                },
                {
                    "name": "size",
                    "field_type": "integer",
                    "min_value": 1,
                    "value": self.get_dict_value("size", self.scenario_dict),
                    "default_value": 1,
                    "help_text": "The number of ensembles in the scenario",
                },
                {
                    "name": "options",
                    "field_type": ScenarioOptionsWidget,
                    "value": {
                        "slice": self.get_dict_value(
                            "slice", self.scenario_dict
                        ),
                        "ensemble_names": self.get_dict_value(
                            "ensemble_names", self.scenario_dict
                        ),
                    },
                    "help_text": "Specify the name of each ensemble (optional) and "
                    "which ensemble to run",
                },
            ]
        }

        super().__init__(
            form_dict=self.scenario_dict,
            model_config=model_config,
            available_fields=available_fields,
            save_button=save_button,
            parent=parent,
        )

    def _check_scenario_name(
        self, name: str, label: str, value: str
    ) -> FormValidation:
        """
        Checks that the new scenario name is not duplicated.
        :param name: The field name.
        :param label: The field label.
        :param value: The parameter name.
        :return: True if the name validates correctly, False otherwise.
        """
        # do not save form if the name is changed and already exists
        if (
            self.name != value
            and self.model_config.scenarios.does_scenario_exist(value) is True
        ):
            return FormValidation(
                validation=False,
                error_message=f"The scenario '{value}; already exists. "
                "Please provide a different name.",
            )
        return FormValidation(validation=True)

    @Slot()
    def on_save(self) -> None:
        """
        Slot called when user clicks on the "Update" button. Only visible fields are
        exported.
        :return: None
        """
        self.logger.debug("Saving form")

        form_data = self.save()
        if form_data is False:
            return

        new_name = form_data["name"]
        # rename scenario
        if form_data["name"] != self.name:
            # update the model configuration
            self.model_config.scenarios.rename(self.name, new_name)

            # update the page name in the list
            self.page.pages.rename_page(self.name, new_name)

            # update the page title
            self.page.set_page_title(new_name)

            # update the scenario list
            scenarios_model: ScenariosListModel = (
                self.page.pages.dialog.list.model
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
        self.dialog.list.update()

        # update tree and status bar
        app = self.dialog.app
        if app is not None:
            if hasattr(app, "components_tree"):
                app.components_tree.reload()
            if hasattr(app, "statusBar"):
                app.statusBar().showMessage(f'Scenario "{self.name}" updated')
