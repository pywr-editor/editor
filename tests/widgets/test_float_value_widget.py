import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from pywr_editor.dialogs import ParameterDialogForm, ParametersDialog
from pywr_editor.form import FloatWidget, FormField, ValueWidget
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogParameterConstantValue:
    """
    Tests the ConstantParameter when user provides a constant value (instead of using
    a table). This also tests other fields (such as scale or offset), which are
    available when ConstantParameter uses a table too.
    """

    model_file = resolve_model_path("model_dialog_parameters.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    def test_parameter(self, qtbot, model_config):
        """
        Tests that the form is correctly filled with the "value" key of the parameter
        and any other fields (scale, offset, etc.)
        """
        dialog = ParametersDialog(model_config, "param1")
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        value_field: FormField = selected_page.findChild(FormField, "value")

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == "param1"
        assert value_field.value() == 4
        assert value_field.message.text() == ""

        # noinspection PyUnresolvedReferences
        assert (
            "Last updated"
            in selected_page.findChild(FormField, "comment").value()
        )
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "scale").value() == 8
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "offset").value() == -1

    def test_float_widget(self, qtbot, model_config):
        """
        Tests that the FloatWidget returns a number when the form is saved.
        """
        param_name = "const_param_with_values"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        value_field: FormField = selected_page.findChild(FormField, "value")
        # noinspection PyTypeChecker
        scale_field: FormField = selected_page.findChild(FormField, "scale")
        # noinspection PyTypeChecker
        value_widget: ValueWidget = value_field.widget
        # noinspection PyTypeChecker
        scale_widget: FloatWidget = scale_field.widget

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name
        scale_widget.line_edit.setText("-100")
        assert scale_widget.validate("scale", "scale", -100).validation is True

        # noinspection PyUnresolvedReferences
        value_widget.line_edit.setText("0.25")
        assert scale_widget.validate("scale", "scale", 0.25).validation is True

        # try saving the form
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert save_button.isEnabled() is True
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert value_field.message.text() == ""
        assert scale_field.message.text() == ""

        assert model_config.has_changes is True
        assert model_config.parameters.get_config_from_name(param_name) == {
            "type": "constant",
            "value": 0.25,
            "scale": -100,
        }

    def test_values_key(self, qtbot, model_config):
        """
        Tests that the form is correctly filled with the "values" key of the parameter.
        """
        dialog = ParametersDialog(model_config, "const_param_with_values")
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        selected_page.findChild(ParameterDialogForm).load_fields()
        value_field = selected_page.findChild(FormField, "value")

        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value()
            == "const_param_with_values"
        )
        # noinspection PyUnresolvedReferences
        assert value_field.value() == 7
        # noinspection PyUnresolvedReferences
        assert value_field.message.text() == ""

    def test_wrong_value_type(self, qtbot, model_config):
        """
        Tests that the form raises a warning if the value type is not a number.
        """
        param_name = "const_param_wrong_type"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        selected_page.findChild(ParameterDialogForm).load_fields()
        # noinspection PyTypeChecker
        value_field: FormField = selected_page.findChild(FormField, "value")
        # noinspection PyTypeChecker
        value_widget: ValueWidget = value_field.widget

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name
        assert value_field.value() == ""
        assert "not valid" in value_field.message.text()

        # validation passes because field is empty at init
        assert (
            value_widget.validate(
                "value", "Value", value_field.value()
            ).validation
            is True
        )

        # try saving the form
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert save_button.isEnabled() is False

        # Change the value and save
        value_widget.line_edit.setText("1")
        assert save_button.isEnabled() is True
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert value_field.message.text() == ""

        assert model_config.has_changes is True
        assert model_config.parameters.get_config_from_name(param_name) == {
            "type": "constant",
            "value": 1.0,
        }

        # Set wrong type again
        value_widget.line_edit.setText("s")
        assert (
            value_widget.validate(
                "value", "Value", value_field.value()
            ).validation
            is False
        )

    @pytest.mark.parametrize(
        "param_name, message",
        [
            ("hydro_param_valid", None),
            # parameter must be between 0 and 1
            ("hydro_param_invalid_min", "is below"),
            ("hydro_param_invalid_max", "is above"),
        ],
    )
    def test_bounds(self, qtbot, model_config, param_name, message):
        """
        Tests the lower and upper bound of the widget at init and when the field is
        validated.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        value_field: FormField = selected_page.findChild(
            FormField, "efficiency"
        )
        # noinspection PyTypeChecker
        value_widget: ValueWidget = value_field.widget

        out = value_widget.validate(
            "efficiency", "Efficiency", value_widget.get_value()
        )
        # valid at init
        if not message:
            assert value_field.message.text() == ""
            assert out.validation is True

            # change to invalid float and validate again
            invalid_float = -10
            value_widget.line_edit.setText(str(invalid_float))
            out = value_widget.validate(
                "efficiency", "Efficiency", invalid_float
            )
            assert out.validation is False
        # invalid at init
        else:
            assert message in value_field.message.text()
            assert out.validation is False
            assert message in out.error_message

    def test_reset(self, qtbot, model_config):
        """
        Tests the reset method.
        """
        param_name = "const_param_with_values"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()
        selected_page = dialog.pages_widget.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        value_field: FormField = selected_page.findChild(FormField, "value")
        # noinspection PyTypeChecker
        value_widget: ValueWidget = value_field.widget

        value_widget.reset()
        assert value_field.message.text() == ""
        assert value_widget.line_edit.text() == ""
