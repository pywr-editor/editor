import pytest

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import FormField, InterpDayWidget
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogParameterInterpDayWidget:
    """
    Tests the InterpDayWidget in the parameter dialog.
    """

    model_file = resolve_model_path("model_dialog_parameters_interp_day_widget.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """

        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, expected",
        [
            ("valid_interp_day", "first"),
            ("valid_interp_day_case", "last"),
            ("valid_interp_day_empty", None),
        ],
    )
    def test_valid_widget(self, qtbot, model_config, param_name, expected):
        """
        Tests that the InterpDayWidget behaves correctly.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        interp_day_field: FormField = selected_page.findChild(FormField, "interp_day")
        interp_day_widget: InterpDayWidget = interp_day_field.widget
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. Test value
        assert interp_day_field.message.text() == ""
        if expected is None:
            assert interp_day_widget.combo_box.currentText() == "None"
            assert interp_day_field.value() is interp_day_widget.get_default_value()
        else:
            assert (
                interp_day_widget.combo_box.currentText()
                == interp_day_widget.value_map[expected]
            )
            assert interp_day_field.value() == expected

        # 2. Reset
        interp_day_widget.reset()
        assert interp_day_widget.combo_box.currentText() == "None"
        assert interp_day_field.value() is interp_day_widget.get_default_value()

    @pytest.mark.parametrize(
        "param_name, message",
        [
            ("invalid_interp_day_wrong_name", "is not valid"),
            ("invalid_interp_day_wrong_type", "is not a valid type"),
        ],
    )
    def test_invalid_widget(self, qtbot, model_config, param_name, message):
        """
        Tests that the InterpDayWidget sets a warning message when the configuration is
        invalid.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        interp_day_field: FormField = selected_page.findChild(FormField, "interp_day")
        interp_day_widget: InterpDayWidget = interp_day_field.widget
        assert selected_page.findChild(FormField, "name").value() == param_name

        # No value is set
        assert message in interp_day_field.message.text()
        assert interp_day_field.value() is interp_day_widget.get_default_value()
        assert interp_day_widget.combo_box.currentText() == "None"
