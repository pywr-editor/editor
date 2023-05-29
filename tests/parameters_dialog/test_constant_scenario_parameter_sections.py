import pytest
from PySide6.QtCore import Qt

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page import ParameterPage
from pywr_editor.form import FormField, ScenarioPickerWidget, TableValuesWidget
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogParameterControlCurveParameterSection:
    """
    Tests the section for parameters supporting scenarios with constant values.
    This is done by testing ConstantScenarioParameter
    """

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(
            resolve_model_path(
                "model_dialog_parameter_constant_scenario_parameter_sections.json"
            )
        )

    @pytest.fixture()
    def model_config_empty(self) -> ModelConfig:
        """
        Initialises the configuration for a model without scenarios.
        :return: The ModelConfig instance.
        """
        return ModelConfig(resolve_model_path("model_4.json"))

    @pytest.mark.parametrize(
        "param_name, selected_scenario, values, validation_message",
        [
            ("valid_scenario", "scenario A", [], None),
            # validation fails
            ("valid_missing_scenario", "None", [], "must select a scenario"),
            ("valid_empty_scenario", "None", [], "must select a scenario"),
        ],
    )
    def test_valid_scenario_picker(
        self,
        qtbot,
        model_config,
        param_name,
        selected_scenario,
        values,
        validation_message,
    ):
        """
        Tests that the values are loaded correctly in the ScenarioPickerWidget.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPage = dialog.pages.currentWidget()
        # noinspection PyTypeChecker
        scenario_field: FormField = selected_page.findChild(FormField, "scenario")
        # noinspection PyTypeChecker
        scenario_widget: ScenarioPickerWidget = scenario_field.widget

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. Check message and value
        assert scenario_field.message.text() == ""
        assert selected_scenario in scenario_widget.combo_box.currentText()
        if selected_scenario == "None":
            assert scenario_field.value() is None
        else:
            assert scenario_field.value() == selected_scenario

        # 2. Validate
        out = scenario_widget.validate("", "", "")
        if validation_message is None:
            assert out.validation is True
        else:
            assert out.validation is False
            assert validation_message in out.error_message

    def test_no_model_scenarios_scenario_picker(self, qtbot, model_config_empty):
        """
        Tests the ScenarioPickerWidget when the model does not contain any scenarios.
        """
        dialog = ParametersDialog(model_config_empty, "param5")
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPage = dialog.pages.currentWidget()

        # scenario field
        # noinspection PyTypeChecker
        scenario_field: FormField = selected_page.findChild(FormField, "scenario")
        # noinspection PyTypeChecker
        scenario_widget: ScenarioPickerWidget = scenario_field.widget

        assert "no scenarios defined" in scenario_field.message.text()
        assert scenario_widget.combo_box.currentText() == "None"
        assert scenario_widget.get_value() is None
        assert scenario_widget.combo_box.isEnabled() is False

    @pytest.mark.parametrize(
        "param_name, init_message, validation_message",
        [
            (
                "invalid_non_existing_scenario",
                "does not exist in the model",
                "must select a scenario",
            ),
            (
                "invalid_scenario_type",
                "must be a string",
                "must select a scenario",
            ),
        ],
    )
    def test_invalid_scenario_picker(
        self,
        qtbot,
        model_config,
        param_name,
        init_message,
        validation_message,
    ):
        """
        Tests the ScenarioPickerWidget when invalid data are given.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPage = dialog.pages.currentWidget()
        # noinspection PyTypeChecker
        field: FormField = selected_page.findChild(FormField, "scenario")
        # noinspection PyTypeChecker
        widget: ScenarioPickerWidget = field.widget

        # 1. Test init message
        if init_message is None:
            assert field.message.text() == ""
        else:
            assert init_message in field.message.text()

        # 2. Test validation message
        out = widget.validate("", "", "")
        assert validation_message in out.error_message

        # 3. Check value in scenario
        assert widget.combo_box.currentText() == "None"
        assert field.value() is None

    @pytest.mark.parametrize(
        "param_name, values, run_validation",
        [
            ("valid_values", [56, 87], True),
            # no init message is displayed, but field would not validate
            ("valid_values_no_scenario", [56, 87], False),
        ],
    )
    def test_valid_scenario_values(
        self, qtbot, model_config, param_name, values, run_validation
    ):
        """
        Tests that the values are loaded correctly in the TableValuesWidget.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPage = dialog.pages.currentWidget()
        # noinspection PyTypeChecker
        values_field: FormField = selected_page.findChild(FormField, "values")
        # noinspection PyTypeChecker
        values_widget: TableValuesWidget = values_field.widget

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. Check message and value
        assert values_field.message.text() == ""
        assert values_field.value() == {"values": values}

        # 2. Validate widget and form to test section filter
        out = values_widget.validate("", "", values_field.value())
        if run_validation:
            assert out.validation is True
            assert values_widget.form.validate() == {
                "name": param_name,
                "scenario": "scenario B",
                "type": "constantscenario",
                "values": values,
            }

        # 3. Change scenario and validate with new size
        if param_name == "valid_values":
            # noinspection PyTypeChecker
            scenario_field: FormField = selected_page.findChild(FormField, "scenario")
            # noinspection PyTypeChecker
            scenario_widget: ScenarioPickerWidget = scenario_field.widget

            selected_index = scenario_widget.combo_box.findData(
                "scenario C", Qt.UserRole
            )
            scenario_widget.combo_box.setCurrentIndex(selected_index)
            out = values_widget.validate("", "", values_field.value())
            assert out.validation is False
            assert "must provide exactly 20" in out.error_message

    @pytest.mark.parametrize(
        "param_name, init_message, validation_message",
        [
            (
                "invalid_values_wrong_size",
                "points must exactly be 10",
                "must provide exactly 10",
            ),
        ],
    )
    def test_invalid_scenario_values(
        self,
        qtbot,
        model_config,
        param_name,
        init_message,
        validation_message,
    ):
        """
        Tests the TableValuesWidget when invalid data are given.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPage = dialog.pages.currentWidget()
        # noinspection PyTypeChecker
        field: FormField = selected_page.findChild(FormField, "values")
        # noinspection PyTypeChecker
        widget: ScenarioPickerWidget = field.widget

        # test init message and validation
        assert init_message in field.message.text()
        out = widget.validate("", "", widget.get_value())
        assert validation_message in out.error_message
