import pytest

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import FormField
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogParameterPolynomial2DCoefficientsWidgetSection:
    """
    Tests the sections for the Polynomial2DStorageParameter.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_polynomial_2d_section.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    def test_valid(self, qtbot, model_config):
        """
        Tests that the field is loaded correctly.
        """
        param_name = "polynomial"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. Check all fields and coefficients
        for form_field in selected_page.findChildren(FormField):
            assert form_field.message.text() == ""
            if form_field.name == "coefficients":
                widget = form_field.widget
                # value
                assert form_field.value() == {
                    widget.var_names[0]: [1.02, 234, 12.56],
                    widget.var_names[1]: [99, -12, 234],
                }
                # validation
                out = widget.validate("", "", widget.get_value())
                assert out.validation is True

        # 2. Validate form to check filter
        form_dict = form.validate()
        assert form_dict == {
            "name": "polynomial",
            "type": "polynomial2dstorage",
            "coefficients": [[1.02, 234, 12.56], [99, -12, 234]],
            "storage_node": "Reservoir",
            "parameter": "value",
        }

    @pytest.mark.parametrize(
        "param_name, init_message, expected",
        [
            (
                "invalid_missing_data",
                "Some values were set to zero",
                [[1.02, 234, 12.56], [99, -12, 0]],
            ),
            (
                "invalid_one_list",
                "Some values were set to zero",
                [[1.02, 234, 12.56], [0, 0, 0]],
            ),
            (
                "invalid_type",
                "data points must be at least 1",
                [[], []],
            ),
        ],
    )
    def test_invalid(
        self, qtbot, model_config, param_name, init_message, expected
    ):
        """
        Tests that the form displays a warning message when the provided value is
        invalid.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. Check field
        form_field = form.find_field_by_name("coefficients")
        widget = form_field.widget
        assert init_message in form_field.message.text()
        assert form_field.value() == {
            widget.var_names[0]: expected[0],
            widget.var_names[1]: expected[1],
        }

        # 2. Validate form to check filter
        if expected[0]:
            form_dict = form.validate()
            assert form_dict == {
                "name": param_name,
                "type": "polynomial2dstorage",
                "coefficients": expected,
                "storage_node": "Reservoir",
                "parameter": "value",
            }
