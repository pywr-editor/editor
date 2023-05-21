from functools import partial

import pytest
from PySide6.QtCore import QTimer

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page_widget import ParameterPageWidget
from pywr_editor.form import FormField
from pywr_editor.model import ModelConfig
from tests.utils import check_msg, close_message_box, resolve_model_path


class TestDialogParameterFlowDelayParameter:
    """
    Tests the section for FlowDelayParameter.
    """

    model_file = resolve_model_path("model_dialog_parameter_flow_delay_section.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, field_name, message",
        [
            ("invalid_timesteps", "timesteps", "must be larger than 1"),
            ("valid_days", "days", None),
            ("invalid_days", "days", "must be exactly divisible by"),
            ("invalid_none_set", None, "You must provide the"),
            ("invalid_both_set", None, "not both values at the same"),
        ],
    )
    def test_validation(self, qtbot, model_config, param_name, field_name, message):
        """
        Tests that the values are loaded correctly.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # send form and verify message in fields
        if field_name is not None:
            form_field = selected_page.form.find_field_by_name(field_name)
            if message is not None:
                QTimer.singleShot(100, close_message_box)
                selected_page.form.validate()
                assert message in form_field.message.text()
            else:
                assert form_field.message.text() == ""
        # validate section
        else:
            if message is not None:
                QTimer.singleShot(100, partial(check_msg, message))
            selected_page.form.validate()
