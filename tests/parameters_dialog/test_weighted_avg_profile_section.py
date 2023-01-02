import pytest
from PySide6.QtCore import QTimer

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page_widget import (
    ParameterPageWidget,
)
from pywr_editor.form import FormField
from pywr_editor.model import ModelConfig
from tests.utils import close_message_box, resolve_model_path


class TestDialogWeightedAverageProfileParameter:
    """
    Tests the sections for the WeightedAverageProfileParameter.
    """

    model_file = resolve_model_path(
        "model_dialog_weighted_avg_parameter_section.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, field_messages",
        [
            ("valid", {"storages": None, "profiles": None}),
            (
                "empty_data",
                {
                    "storages": "The field cannot be empty",
                    "profiles": "The field cannot be empty",
                },
            ),
            (
                "wrong_profile_count",
                {"profiles": "The number of profiles (1) must equal the"},
            ),
        ],
    )
    def test_validation(self, qtbot, model_config, param_name, field_messages):
        """
        Tests that the values are loaded correctly.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        for field_name_to_check, message in field_messages.items():
            # send form and verify message
            form_field = selected_page.form.find_field_by_name(
                field_name_to_check
            )

            if message is not None:
                QTimer.singleShot(100, close_message_box)
                selected_page.form.validate()
                assert message in form_field.message.text()
            else:
                assert form_field.message.text() == ""
