import pytest

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page import ParameterPage
from pywr_editor.form import (
    FormField,
    ScenarioValuesWidget,
    SourceSelectorWidget,
    UrlWidget,
    ValuesAndExternalDataWidget,
)
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogParameterArrayIndexedScenarioMonthlyFactorsParameterSection:
    """
    Tests the section for ArrayIndexedScenarioMonthlyFactorsParameter.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_array_indexed_scenario_factors_section.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, field_name, init_message, validation_message",
        [
            # values must match at least number of time steps
            (
                "invalid_min_value_size",
                "ts_values",
                "points must be at least 15705",
                "provide at least 15705 values",
            ),
            (
                "invalid_factor_size",
                "values",
                "as many ensembles as the scenario size (2)",
                None,
            ),
        ],
    )
    def test_invalid_and_form_filter(
        self,
        qtbot,
        model_config,
        param_name,
        field_name,
        init_message,
        validation_message,
    ):
        """
        Tests when the parameter data are not valid and the section filter method.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPage = dialog.pages.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        form_field: FormField = selected_page.findChild(FormField, field_name)
        # noinspection PyTypeChecker
        widget: ValuesAndExternalDataWidget | ScenarioValuesWidget = form_field.widget

        # 1. Check message at init
        assert init_message in form_field.message.text()

        # 2. Check validation message
        if validation_message is not None:
            out = widget.validate("", "", form_field.value())
            assert validation_message in out.error_message

        # 3. Test filter method
        if param_name == "invalid_min_value_size":
            # A. Set the correct number of values
            new_values = list(range(0, 15705))
            widget.model.values[0] = new_values

            assert form_field.form.validate() == {
                "name": param_name,
                "type": "arrayindexedscenariomonthlyfactors",
                "scenario": "scenario A",
                "values": new_values,
                "factors": [
                    [0, 2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                    [0, 2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                ],
            }

            # B. Set anonymous table
            # noinspection PyTypeChecker
            source_widget: SourceSelectorWidget = selected_page.findChild(
                SourceSelectorWidget
            )
            source_widget.combo_box.setCurrentText(
                source_widget.labels["anonymous_table"]
            )
            # noinspection PyTypeChecker
            url_widget: UrlWidget = selected_page.findChild(UrlWidget)
            url_widget.line_edit.setText("files/table.csv")

            assert form_field.form.validate() == {
                "name": param_name,
                "type": "arrayindexedscenariomonthlyfactors",
                "scenario": "scenario A",
                "values": new_values,
                "factors": {"url": "files/table.csv"},
            }
