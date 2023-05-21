import pytest

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import FormField, ParameterAggFuncWidget
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogThresholdRelationSymbolWidget:
    """
    Tests the ParameterAggFuncWidget.
    """

    model_file = resolve_model_path("model_dialog_parameter_agg_func_widget.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, label",
        [
            ("valid_func1", "Sum"),
            ("valid_func2", "Product"),
            ("valid_func3", "Mean"),
            ("not_provided", "Sum"),
        ],
    )
    def test_valid_values(self, qtbot, model_config, param_name, label):
        """
        Tests that the values are loaded correctly.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        func_field: FormField = selected_page.findChild(FormField, "agg_func")
        # noinspection PyTypeChecker
        func_widget: ParameterAggFuncWidget = func_field.widget

        assert func_field.message.text() == ""

        # check values in combobox
        assert func_widget.combo_box.currentText() == label
        assert func_widget.get_value() == label.lower()

    @pytest.mark.parametrize(
        "param_name, message",
        [
            ("wrong_func", "does not exist"),
            ("wrong_type", "is not a valid"),
            ("empty_string", "is not a valid type"),
        ],
    )
    def test_invalid_values(self, qtbot, model_config, param_name, message):
        """
        Tests that the warning message is shown when the values are not valid.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        func_field: FormField = selected_page.findChild(FormField, "agg_func")
        # noinspection PyTypeChecker
        func_widget: ParameterAggFuncWidget = func_field.widget

        # check value in combobox
        assert (
            func_widget.combo_box.currentText()
            == func_widget.get_default_selection().title()
        )
        assert func_widget.get_value() == func_widget.get_default_selection().lower()

        # check warning
        assert message in func_field.message.text()
