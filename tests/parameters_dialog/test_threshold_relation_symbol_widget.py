import pytest

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import FormField, ThresholdRelationSymbolWidget
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogThresholdRelationSymbolWidget:
    """
    Tests the ThresholdRelationSymbolWidget.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_threshold_relation_symbol_widget.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, label, symbol",
        [
            # sign as string
            ("valid_symbol1", "Equal (=)", "EQ"),
            # sign
            ("valid_symbol_sign", "Less (<)", "LT"),
        ],
    )
    def test_valid_values(self, qtbot, model_config, param_name, label, symbol):
        """
        Tests that the values are loaded correctly.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyUnresolvedReferences
        symbol_field: FormField = selected_page.findChild(FormField, "predicate")
        # noinspection PyUnresolvedReferences
        symbol_widget: ThresholdRelationSymbolWidget = symbol_field.widget

        assert symbol_field.message.text() == ""

        # check values in combobox
        assert symbol_widget.combo_box.currentText() == label
        assert symbol_widget.get_value() == symbol

    @pytest.mark.parametrize(
        "param_name, message",
        [
            # empty string treated as None
            ("empty_string", ""),
            ("wrong_symbol", "does not exist"),
            ("not_provided", ""),
            ("wrong_type", "is not a valid type"),
        ],
    )
    def test_invalid_values(self, qtbot, model_config, param_name, message):
        """
        Tests that the warning message is shown when the values are not valid.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyUnresolvedReferences
        symbol_field: FormField = selected_page.findChild(FormField, "predicate")
        # noinspection PyUnresolvedReferences
        symbol_widget: ThresholdRelationSymbolWidget = symbol_field.widget

        # check value in combobox
        assert (
            symbol_widget.combo_box.currentText()
            == symbol_widget.labels_map[symbol_widget.get_default_selection()]
        )
        assert symbol_widget.get_value() == symbol_widget.get_default_selection()

        # check warning
        assert message in symbol_field.message.text()
