import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QPushButton

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page_widget import (
    ParameterPageWidget,
)
from pywr_editor.form import FormField
from pywr_editor.model import ModelConfig
from tests.utils import close_message_box, resolve_model_path


class TestDialogParameterControlCurveParameterSection:
    """
    Tests the sections for the ControlCurveParameter parameter.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_control_curves_sections.json"
    )

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
            # constant control curve with "values"
            (
                "valid_with_constant_control_curve_and_values",
                {
                    "type": "controlcurve",
                    "storage_node": "Reservoir",
                    "control_curve": {"type": "constant", "value": 12},
                    "values": [12, 45],
                },
            ),
            # parametric control curve with "values"
            (
                "valid_with_parametric_control_curve_and_values",
                {
                    "type": "controlcurve",
                    "storage_node": "Reservoir",
                    "values": [12, 45],
                    "control_curve": {
                        "type": "NodeThresholdParameter",
                        "node": "Link",
                        "threshold": 75.32,
                        "values": [3, 4],
                    },
                },
            ),
            (
                "valid_with_constant_control_curve_and_param",
                {
                    "type": "controlcurve",
                    "storage_node": "Reservoir",
                    "control_curve": {"type": "constant", "value": 12},
                    "parameters": [
                        {"type": "constant", "value": 12},
                        {"type": "constant", "value": 67},
                    ],
                },
            ),
            # "values" key is prioritised
            (
                "valid_with_values_and_param",
                {
                    "type": "controlcurve",
                    "storage_node": "Reservoir",
                    "control_curve": {"type": "constant", "value": 12},
                    "values": [12, 67],
                },
            ),
            # list in "control_curves" key convert to "control_curve
            (
                "valid_with_control_curves_to_one",
                {
                    "type": "controlcurve",
                    "storage_node": "Reservoir",
                    "control_curve": {"type": "constant", "value": 12},
                    "values": [12, 67],
                },
            ),
        ],
    )
    def test_valid(self, qtbot, model_config, param_name, expected):
        """
        Tests that the values are loaded correctly.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        param_dict = model_config.parameters.get_config_from_name(param_name)
        source_field = form.find_field_by_name("values_source")
        # check for initial warnings
        for form_field in selected_page.findChildren(FormField):
            form_field: FormField
            widget = form_field.widget
            assert form_field.message.text() == ""

            # check field visibility
            if form_field.name == "values":
                is_values_selected = source_field.value() == "values"
                assert form_field.isVisible() is is_values_selected
                assert (
                    form.find_field_by_name("parameters").isVisible()
                    is not is_values_selected
                )
            elif form_field.name == "parameters":
                is_parameters_selected = source_field.value() == "parameters"
                assert form_field.isVisible() is is_parameters_selected
                assert (
                    form.find_field_by_name("values").isVisible()
                    is not is_parameters_selected
                )

            # test validation
            if hasattr(widget, "get_value"):
                widget_value = widget.get_value()
                out = widget.validate("", "", widget_value)

                assert out.validation is True
                # check source for values
                if form_field.name == "values_source":
                    if "values" in param_dict:
                        assert widget_value == "values"
                    else:
                        assert widget_value == "parameters"

        # enable submit button and send form for validation to test filter
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert (
            model_config.parameters.get_config_from_name(param_name) == expected
        )

    @pytest.mark.parametrize(
        "param_name, field_with_error, message",
        [
            (
                "invalid_with_not_enough_params",
                "parameters",
                "The number of parameters must be 2",
            ),
            (
                "invalid_with_empty_params",
                "parameters",
                "The number of parameters must be 2",
            ),
            (
                "invalid_with_not_enough_values",
                "values",
                "The number of values must be 3",
            ),
        ],
    )
    def test_invalid(
        self, qtbot, model_config, param_name, field_with_error, message
    ):
        """
        Tests the widget when an invalid configuration is used.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # send form and verify message
        QTimer.singleShot(100, close_message_box)
        selected_page.form.validate()
        form_field: FormField = selected_page.form.find_field_by_name(
            field_with_error
        )
        assert message in form_field.message.text()

    @pytest.mark.parametrize(
        "param_name, message",
        # bounds provided but 'variable_indices' is missing
        [
            (
                "bounds_no_variable_indices",
                "you have set the 'Variable indices'",
            ),
            # bounds, 'variable_indices' but 'values' is missing
            ("bounds_no_values_set", "you have set the 'Constant values'"),
            # all mandatory fields are set, but bound size is wrong
            ("bounds_wrong_size", "be the same as the number of indices"),
            # validation passes
            ("bounds_ok", None),
        ],
    )
    def test_opt_bounds_validation(self, model_config, param_name, message):
        """
        Tests the validation of ControlCurveOptBoundsWidget
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        bounds_field: FormField = selected_page.form.find_field_by_name(
            "lower_bounds"
        )

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # send form and verify message
        if message is not None:
            QTimer.singleShot(100, close_message_box)
            selected_page.form.validate()
            assert message in bounds_field.message.text()
        else:
            assert bounds_field.message.text() == ""
