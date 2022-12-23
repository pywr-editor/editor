import pytest
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QPushButton

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page_widget import (
    ParameterPageWidget,
)
from pywr_editor.form import (
    FormField,
    MonthlyValuesWidget,
    ScenarioPickerWidget,
    ScenarioValuesPickerDialogWidget,
    ScenarioValuesWidget,
    SourceSelectorWidget,
    TableSelectorWidget,
    UrlWidget,
)
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogParameterControlCurveParameterSection:

    """
    Tests the sections for parameters supporting scenario values using
    ScenarioValuesWidget. This is done by testing
    ScenarioMonthlyProfileParameterSection and ArrayIndexedScenarioParameterSection
    """

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(
            resolve_model_path(
                "model_dialog_parameter_scenario_parameter_sections.json"
            )
        )

    @pytest.mark.parametrize(
        "param_name",
        [
            "valid_values",
            # values not provided - only validation fails
            "valid_no_values",
            # valid values are passed - validation of scenario size at init is skipped
            "valid_values_no_scenario",
        ],
    )
    def test_valid_annual_profile_scenario_values(
        self, qtbot, model_config, param_name
    ):
        """
        Tests that the values are loaded correctly in the ScenarioValuesWidget for an
        annual profile.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        values_field: FormField = selected_page.findChild(FormField, "values")
        # noinspection PyTypeChecker
        values_widget: ScenarioValuesWidget = values_field.widget

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. Check message, value and validate
        assert values_field.message.text() == ""
        out = values_widget.validate("", "", values_field.value())

        # 2. Check value, validation and section filter
        if param_name == "valid_values":
            values = [list(range(1, 13)), list(range(10, 130, 10))]
            assert values_field.value() == values
            assert out.validation is True
            # test section filter
            assert values_widget.form.validate() == {
                "name": param_name,
                "scenario": "scenario B",
                "type": "scenariomonthlyprofile",
                "values": values,
            }
        elif param_name == "valid_no_values":
            assert "must provide the values" in out.error_message

        # 3. Change scenario and validate with new size
        if param_name == "valid_values":
            # noinspection PyTypeChecker
            scenario_field: FormField = selected_page.findChild(
                FormField, "scenario"
            )
            # noinspection PyTypeChecker
            scenario_widget: ScenarioPickerWidget = scenario_field.widget
            assert values_widget.scenario_size == 2

            selected_index = scenario_widget.combo_box.findData(
                "scenario C", Qt.UserRole
            )
            scenario_widget.combo_box.setCurrentIndex(selected_index)
            assert values_widget.scenario_size == 20
            out = values_widget.validate("", "", [])
            assert out.validation is False
            assert (
                "many ensembles as the scenario size (20)" in out.error_message
            )

        # 4. Reset
        values_widget.reset()
        assert values_widget.get_value() == []

    @pytest.mark.parametrize(
        "param_name, init_message, validation_message",
        [
            (
                "invalid_type",
                "must be a list",
                "must provide the values",
            ),
            (
                "invalid_no_nested_lists",
                "can contain only lists",
                "must provide the values",
            ),
            (
                "invalid_only_numbers_str",
                "can contain only numbers",
                "must provide the values",
            ),
            (
                "invalid_only_numbers_bool",
                "can contain only numbers",
                "must provide the values",
            ),
            (
                "invalid_only_numbers_null",
                "can contain only numbers",
                "must provide the values",
            ),
            (
                "invalid_profile_size",
                "ensemble must exactly have 12 numbers",
                "ensemble must exactly have 12 numbers",
            ),
            (
                "invalid_scenario_size",
                "as many ensembles as the scenario size (2)",
                "as many ensembles as the scenario size (2)",
            ),
            # two init messages
            (
                "invalid_profile_and_scenario_size",
                [
                    "ensemble must exactly have 12 numbers",
                    "as many ensembles as the scenario size (2)",
                ],
                "ensemble must exactly have 12 numbers",
            ),
        ],
    )
    def test_invalid_annual_profile_scenario_values(
        self, qtbot, model_config, param_name, init_message, validation_message
    ):
        """
        Tests the ScenarioValuesWidget when invalid data are given for an annual
        profile.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        field: FormField = selected_page.findChild(FormField, "values")
        # noinspection PyTypeChecker
        widget: ScenarioPickerWidget = field.widget

        # test init message and validation
        if isinstance(init_message, str):
            assert init_message in field.message.text()
        elif isinstance(init_message, list):
            for sub_msg in init_message:
                assert sub_msg in field.message.text()

        out = widget.validate("", "", widget.get_value())
        assert validation_message in out.error_message

    @staticmethod
    def select_row(widget: ScenarioValuesWidget, row_id: int) -> None:
        """
        Selects a row in the ListView.
        :param widget: The widget instance.
        :param row_id: The row number ot select.
        :return: None
        """
        widget.list.clearSelection()
        row = widget.model.index(row_id, 0)
        widget.list.selectionModel().select(row, QItemSelectionModel.Select)

    def test_delete(self, qtbot, model_config):
        """
        Tests ensemble values deletion.
        """
        param_name = "invalid_scenario_size"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        values_field: FormField = selected_page.findChild(FormField, "values")
        # noinspection PyTypeChecker
        values_widget: ScenarioValuesWidget = values_field.widget
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )

        # 1. delete button is disabled
        assert values_widget.list.selectionModel().selection().count() == 0
        assert values_widget.delete_button.isEnabled() is False
        assert save_button.isEnabled() is False

        # 2. Delete last ensemble. Button up is still disabled
        self.select_row(values_widget, 2)
        assert values_widget.delete_button.isEnabled() is True
        qtbot.mouseClick(values_widget.delete_button, Qt.MouseButton.LeftButton)
        new_value = [list(range(1, 13)), list(range(10, 130, 10))]
        assert values_widget.get_value() == new_value

        # 3. Save the entire form
        # noinspection PyTypeChecker
        main_save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert "Update" in main_save_button.text()

        # button in parent form is enabled as soon as the child form is saved
        assert main_save_button.isEnabled() is True
        qtbot.mouseClick(main_save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert model_config.parameters.get_config_from_name(param_name) == {
            "type": "scenariomonthlyprofile",
            "scenario": "scenario B",
            "values": new_value,
        }

    @pytest.mark.parametrize(
        "mode",
        ["add", "edit"],
    )
    def test_add_edit_ensemble_values(self, qtbot, model_config, mode):
        """
        Tests when values are added or edited for an ensemble.
        """
        param_name = "valid_values"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        values_field: FormField = selected_page.findChild(FormField, "values")
        # noinspection PyTypeChecker
        values_widget: ScenarioValuesWidget = values_field.widget

        # 1. Open the dialog
        index = None
        if mode == "edit":
            index = 1
            self.select_row(values_widget, index)
            qtbot.mouseClick(
                values_widget.edit_button, Qt.MouseButton.LeftButton
            )
        elif mode == "add":
            qtbot.mouseClick(
                values_widget.add_button, Qt.MouseButton.LeftButton
            )
        else:
            raise ValueError("Mode not supported")

        # noinspection PyTypeChecker
        child_dialog: ScenarioValuesPickerDialogWidget = (
            selected_page.findChild(ScenarioValuesPickerDialogWidget)
        )
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(
            QPushButton, "save_button"
        )

        # 2. Add/change values by manipulating the model
        # noinspection PyTypeChecker
        monthly_values_widget: MonthlyValuesWidget = child_dialog.findChild(
            MonthlyValuesWidget
        )
        if mode == "edit":
            new_values = monthly_values_widget.model.values
            new_values[5] = -999
            monthly_values_widget.model.values = new_values
        else:
            new_values = [23.41] * 12
        monthly_values_widget.model.values = new_values

        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        # manually close the dialog
        child_dialog.close()

        # 3. Check the model in the parent dialog
        new_model_values = [list(range(1, 13)), list(range(10, 130, 10))]
        if mode == "add":
            new_model_values.append(new_values)
            # ensure that the list size equals the scenarios size
            del values_widget.model.values[0]
            del new_model_values[0]
        else:
            new_model_values[index] = new_values

        assert values_widget.get_value() == new_model_values

        # 4. Save the entire form
        # noinspection PyTypeChecker
        main_save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert "Update" in main_save_button.text()

        # button in parent form is enabled as soon as the child form is saved
        assert main_save_button.isEnabled() is True
        qtbot.mouseClick(main_save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert model_config.parameters.get_config_from_name(param_name) == {
            "type": "scenariomonthlyprofile",
            "scenario": "scenario B",
            "values": new_model_values,
        }

    def test_use_model_table(self, qtbot, model_config):
        """
        Tests when values are fetched from a model table.
        """
        param_name = "valid_values"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. Change the source
        # noinspection PyUnresolvedReferences
        source_widget: SourceSelectorWidget = selected_page.findChild(
            FormField, "source"
        ).widget
        source_widget.combo_box.setCurrentText(source_widget.labels["table"])

        # 2. Set the table
        # noinspection PyUnresolvedReferences
        table_widget: TableSelectorWidget = selected_page.findChild(
            FormField, "table"
        ).widget
        table_widget.combo_box.setCurrentText("Table 1")

        # 3. Save the entire form
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert "Update" in save_button.text()
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert model_config.parameters.get_config_from_name(param_name) == {
            "type": "scenariomonthlyprofile",
            "scenario": "scenario B",
            "table": "Table 1",
        }

    def test_use_url(self, qtbot, model_config):
        """
        Tests when values are fetched from an external file.
        """
        param_name = "valid_values"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. Change the source
        # noinspection PyUnresolvedReferences
        source_widget: SourceSelectorWidget = selected_page.findChild(
            FormField, "source"
        ).widget
        source_widget.combo_box.setCurrentText(
            source_widget.labels["anonymous_table"]
        )

        # 2. Set the URL
        csv_file = "files/table.csv"
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget
        url_widget.line_edit.setText(csv_file)

        # 3. Save the entire form
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert "Update" in save_button.text()
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert model_config.parameters.get_config_from_name(param_name) == {
            "type": "scenariomonthlyprofile",
            "scenario": "scenario B",
            "url": csv_file,
        }

    @pytest.mark.parametrize(
        "param_name, valid, init_message, validation_message",
        [
            ("valid_array_indexed_scenario", True, None, None),
            (
                "invalid_array_indexed_scenario",
                False,
                "ensemble must have at least 5 numbers",
                "ensemble must have at least 5 numbers",
            ),
        ],
    )
    def test_array_indexed_scenario(
        self,
        qtbot,
        model_config,
        param_name,
        valid,
        init_message,
        validation_message,
    ):
        """
        Tests the ScenarioValuesWidget when used with an ArrayIndexedScenarioParameter.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        values_field: FormField = selected_page.findChild(FormField, "values")
        # noinspection PyTypeChecker
        values_widget: ScenarioValuesWidget = values_field.widget

        out = values_widget.validate("", "", values_field.value())
        if valid:
            # 1. Check message, value and validate
            assert values_field.message.text() == ""

            # 2. Check value, validation and section filter
            values = [[1, 6, 19, 5, 21], [10, 60, 190, 23, 65]]
            assert values_field.value() == values
            assert out.validation is True
            # test section filter
            assert values_widget.form.validate() == {
                "name": param_name,
                "scenario": "scenario B",
                "type": "arrayindexedscenario",
                "values": values,
            }
        else:
            # Check messages
            assert init_message in values_field.message.text()
            assert validation_message in out.error_message
