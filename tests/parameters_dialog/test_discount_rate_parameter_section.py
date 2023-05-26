import pytest
from PySide6.QtCore import QTimer

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page_widget import ParameterPageWidget
from pywr_editor.form import FormField
from pywr_editor.model import ModelConfig
from tests.utils import close_message_box, resolve_model_path


class TestDialogParameterControlCurveParameterSection:
    """
    Tests the section for PiecewiseIntegralParameter.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_discount_rate_parameter_section.json"
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
            ("valid", "discount_rate", None),
            (
                "invalid_discount_rate",
                "discount_rate",
                "must be between 0 and 1",
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
