import pytest
from PySide6.QtCore import QTimer
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page_widget import (
    ParameterPageWidget,
)
from pywr_editor.form import FormField
from tests.utils import resolve_model_path, close_message_box


class TestDialogParameterControlCurveParameterSection:
    """
    Tests the section for PiecewiseIntegralParameter.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_piecewise_integral_parameter_section.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, field_name_to_check, message",
        [
            ("valid", "x_y_values", None),
            ("invalid_size_of_x", "x_y_values", "must provide at least 2"),
            ("invalid_negative_x", "x_y_values", "must start from zero"),
            (
                "invalid_not_increasing_x",
                "x_y_values",
                "must be strictly monotonically increasing",
            ),
        ],
    )
    def test_validation(
        self, qtbot, model_config, param_name, field_name_to_check, message
    ):
        """
        Tests that the values are loaded correctly.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # send form and verify message
        form_field = selected_page.form.find_field_by_name(field_name_to_check)

        if message is not None:
            QTimer.singleShot(100, close_message_box)
            selected_page.form.validate()
            assert message in form_field.message.text()
        else:
            assert form_field.message.text() == ""

    def test_filter(self, qtbot, model_config):
        """
        Tests the filter method.
        """
        param_name = "valid"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # test filter that splits x and y
        assert selected_page.form.validate() == {
            "name": param_name,
            "type": "piecewiseintegral",
            "x": [67, 98, 123],
            "y": [43, 0.5, 0.1],
            "parameter": 47,
        }
