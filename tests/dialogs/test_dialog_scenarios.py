import pytest
from PySide6.QtCore import QItemSelectionModel, Qt, QTimer
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from pywr_editor.dialogs import ScenariosDialog
from pywr_editor.dialogs.scenarios.scenario_empty_page_widget import (
    ScenarioEmptyPageWidget,
)
from pywr_editor.dialogs.scenarios.scenario_form_widget import ScenarioFormWidget
from pywr_editor.form import FormField
from pywr_editor.model import ModelConfig
from tests.utils import close_message_box, resolve_model_path


class TestScenariosDialog:
    """
    Tests the general behaviour of the scenario dialog (when adding or deleting
    scenarios, etc.)
    """

    model_file = resolve_model_path("model_1.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.fixture()
    def dialog(self, model_config) -> ScenariosDialog:
        """
        Initialises the dialog.
        :param model_config: The ModelConfig instance.
        :return: The ScenariosDialog instance.
        """
        dialog = ScenariosDialog(model_config)
        dialog.show()
        return dialog

    def test_add_new_scenario(self, qtbot, model_config, dialog):
        """
        Tests that a new scenario can be correctly added.
        """
        scenario_list_widget = dialog.scenarios_list_widget
        pages_widget = dialog.pages
        add_button: QPushButton = pages_widget.empty_page.findChild(
            QPushButton, "add_button"
        )

        qtbot.mouseClick(add_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        # new name is random
        new_name = list(pages_widget.pages.keys())[-1]

        # Scenario model
        # the scenario is added to the model internal list
        assert new_name in scenario_list_widget.model.scenario_names
        # the scenario appears in the parameters list on the left-hand side of the
        # dialog
        new_model_index = scenario_list_widget.model.index(
            model_config.scenarios.count - 1, 0
        )
        assert new_model_index.data() == new_name
        # the item is selected
        assert scenario_list_widget.list.selectedIndexes()[0].data() == new_name
        # Page widget
        selected_page = pages_widget.currentWidget()
        selected_page.findChild(ScenarioFormWidget).load_fields()
        assert new_name in selected_page.findChild(QLabel).text()
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")
        # button is disabled
        assert save_button.isEnabled() is False

        # the scenario is in the widgets list
        assert new_name in pages_widget.pages.keys()
        # the form page is selected
        assert selected_page == pages_widget.pages[new_name]
        # the form is filled with the name
        # noinspection PyTypeChecker
        name_field: FormField = selected_page.findChild(FormField, "name")
        assert name_field.value() == new_name

        # the model is updated
        assert model_config.has_changes is True
        assert model_config.scenarios.exists(new_name) is True
        assert model_config.scenarios.config(new_name) == {
            "name": new_name,
        }

        # rename and save
        renamed_scenario_name = "A new shiny name"
        name_field.widget.setText(renamed_scenario_name)

        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert name_field.message.text() == ""

        # the page widget is renamed
        assert renamed_scenario_name in pages_widget.pages.keys()
        assert renamed_scenario_name in selected_page.findChild(QLabel).text()

        # model configuration
        assert model_config.scenarios.exists(new_name) is False
        assert model_config.scenarios.exists(renamed_scenario_name) is True
        assert model_config.scenarios.config(renamed_scenario_name) == {
            "name": renamed_scenario_name
        }

    def test_rename_parameter(self, qtbot, model_config, dialog):
        """
        Tests that a scenario is renamed correctly.
        """
        current_name = "scenario B"
        new_name = "scenario X"
        pages_widget = dialog.pages

        # select the scenario
        pages_widget.set_current_widget_by_name(current_name)
        selected_page = pages_widget.currentWidget()
        selected_page.form.load_fields()
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")
        name_field: FormField = selected_page.findChild(FormField, "name")

        # 1. Change the name and save
        assert name_field.value() == current_name
        name_field.widget.setText(new_name)

        qtbot.wait(200)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert name_field.message.text() == ""
        assert selected_page.findChild(FormField, "name").message.text() == ""

        # the page widget is renamed
        assert new_name in pages_widget.pages.keys()
        assert new_name in selected_page.findChild(QLabel).text()

        # model has changes
        assert model_config.has_changes is True
        assert model_config.scenarios.exists(current_name) is False
        assert model_config.scenarios.exists(new_name) is True
        assert model_config.scenarios.config(new_name) == {
            "name": new_name,
            "size": 2,
            "ensemble_names": ["First", "Second"],
        }

        # 2. Set duplicated name
        name_field.widget.setText("scenario A")
        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert "already exists" in name_field.message.text()
        assert new_name in model_config.scenarios.names

    def test_delete_scenarios(self, qtbot, model_config, dialog):
        """
        Tests that a scenario is deleted correctly.
        """
        deleted_scenario = "scenario A"
        scenario_list_widget = dialog.scenarios_list_widget
        pages_widget = dialog.pages

        # select a parameter from the list
        model_index = scenario_list_widget.model.index(0, 0)
        assert model_index.data() == deleted_scenario
        scenario_list_widget.list.selectionModel().select(
            model_index, QItemSelectionModel.Select
        )

        # delete button is enabled and the item is selected
        delete_button: QPushButton = pages_widget.pages[deleted_scenario].findChild(
            QPushButton, "delete_button"
        )
        assert delete_button.isEnabled() is True
        assert scenario_list_widget.list.selectedIndexes()[0].data() == deleted_scenario

        # delete
        def confirm_deletion():
            widget = QApplication.activeModalWidget()
            qtbot.mouseClick(widget.findChild(QPushButton), Qt.MouseButton.LeftButton)

        QTimer.singleShot(100, confirm_deletion)
        qtbot.mouseClick(delete_button, Qt.MouseButton.LeftButton)

        assert isinstance(pages_widget.currentWidget(), ScenarioEmptyPageWidget)
        assert deleted_scenario not in pages_widget.pages.keys()
        assert model_config.scenarios.exists(deleted_scenario) is False
        assert deleted_scenario not in scenario_list_widget.model.scenario_names
