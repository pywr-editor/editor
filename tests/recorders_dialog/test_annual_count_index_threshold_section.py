import pytest
from PySide6.QtCore import QTimer

from pywr_editor.dialogs import RecordersDialog
from pywr_editor.dialogs.recorders.recorder_page_widget import RecorderPageWidget
from pywr_editor.form import FormField
from pywr_editor.model import ModelConfig
from tests.utils import close_message_box, resolve_model_path


class TestDialogRecorderAnnualCountIndexThresholdRecorderSection:
    """
    Tests the AnnualCountIndexThresholdRecorderSection.
    """

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(
            resolve_model_path(
                "model_dialog_recorders_annual_count_index_threshold_section.json"
            )
        )

    @pytest.mark.parametrize(
        "recorder_name, expected_months, validation_message",
        [
            ("valid_months", [1, 2], None),
            ("invalid_months_1", [0, 5], "month numbers are not valid"),
            ("invalid_months_2", [1, 20], "month numbers are not valid"),
        ],
    )
    def test_months_validation(
        self,
        qtbot,
        model_config,
        recorder_name,
        expected_months,
        validation_message,
    ):
        """
        Tests the "exclude_months" field validation method.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == recorder_name

        # 1. Check value
        field = form.find_field_by_name("exclude_months")
        assert field.value() == expected_months

        # 2. Validate form
        if validation_message is None:
            assert form.validate() is not False
        else:
            QTimer.singleShot(100, close_message_box)
            form.validate()
            assert validation_message in field.message.text()
