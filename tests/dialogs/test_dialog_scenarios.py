import pytest
from PySide6.QtCore import Qt, QTimer, QItemSelectionModel
from PySide6.QtWidgets import QLabel, QPushButton, QApplication
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import ScenariosDialog
from pywr_editor.dialogs.scenarios.scenario_form_widget import (
    ScenarioFormWidget,
)
from pywr_editor.dialogs.scenarios.scenario_empty_page_widget import (
    ScenarioEmptyPageWidget,
)

from pywr_editor.form import FormField
from tests.utils import resolve_model_path, close_message_box


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
        dialog.hide()
        return dialog

    def test_add_new_scenario(self, qtbot, model_config, dialog):
        """
        Tests that a new scenario can be correctly added.
        """
        scenario_list_widget = dialog.list
        pages_widget = dialog.pages
        qtbot.mouseClick(
            scenario_list_widget.add_button, Qt.MouseButton.LeftButton
        )
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
        assert (
            scenario_list_widget.list.selectionModel().isSelected(
                new_model_index
            )
            is True
        )

        # Page widget
        selected_page = pages_widget.currentWidget()
        selected_page.findChild(ScenarioFormWidget).load_fields()
        assert new_name in selected_page.findChild(QLabel).text()
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
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
        assert model_config.scenarios.does_scenario_exist(new_name) is True
        assert model_config.scenarios.get_config_from_name(new_name) == {
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
        assert model_config.scenarios.does_scenario_exist(new_name) is False
        assert (
            model_config.scenarios.does_scenario_exist(renamed_scenario_name)
            is True
        )
        assert model_config.scenarios.get_config_from_name(
            renamed_scenario_name
        ) == {"name": renamed_scenario_name}

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
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        name_field: FormField = selected_page.findChild(FormField, "name")

        # 1. Change the name and save
        assert name_field.value() == current_name
        name_field.widget.setText(new_name)

        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert name_field.message.text() == ""
        assert selected_page.findChild(FormField, "name").message.text() == ""

        # the page widget is renamed
        assert new_name in pages_widget.pages.keys()
        assert new_name in selected_page.findChild(QLabel).text()

        # model has changes
        assert model_config.has_changes is True
        assert model_config.scenarios.does_scenario_exist(current_name) is False
        assert model_config.scenarios.does_scenario_exist(new_name) is True
        assert model_config.scenarios.get_config_from_name(new_name) == {
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
        scenario_list_widget = dialog.list
        pages_widget = dialog.pages

        # select a parameter from the list
        model_index = scenario_list_widget.model.index(0, 0)
        assert model_index.data() == deleted_scenario
        scenario_list_widget.list.selectionModel().select(
            model_index, QItemSelectionModel.Select
        )

        # delete button is enabled and the item is selected
        assert scenario_list_widget.delete_button.isEnabled() is True
        assert (
            scenario_list_widget.list.selectionModel().isSelected(model_index)
            is True
        )

        # delete
        def confirm_deletion():
            widget = QApplication.activeModalWidget()
            qtbot.mouseClick(
                widget.findChild(QPushButton), Qt.MouseButton.LeftButton
            )

        QTimer.singleShot(100, confirm_deletion)
        qtbot.mouseClick(
            scenario_list_widget.delete_button, Qt.MouseButton.LeftButton
        )

        assert isinstance(pages_widget.currentWidget(), ScenarioEmptyPageWidget)
        assert deleted_scenario not in pages_widget.pages.keys()
        assert (
            model_config.scenarios.does_scenario_exist(deleted_scenario)
            is False
        )
        assert deleted_scenario not in scenario_list_widget.model.scenario_names
