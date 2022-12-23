import pytest
from PySide6.QtCore import QTimer

from pywr_editor.dialogs import RecordersDialog
from pywr_editor.dialogs.recorders.recorder_page_widget import (
    RecorderPageWidget,
)
from pywr_editor.form import FormField
from pywr_editor.model import ModelConfig
from tests.utils import close_message_box, resolve_model_path


class TestDialogRecorderStorageDurationCurveRecorderSection:
    """
    Tests the StorageDurationCurveRecorder.
    """

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(
            resolve_model_path(
                "model_dialog_recorders_storage_duration_curve_section.json"
            )
        )

    @pytest.mark.parametrize(
        "recorder_name, expected_percentiles, validation_message",
        [
            ("valid_percentiles", [1, 30, 50, 80, 95], None),
            (
                "invalid_percentiles",
                [30, 30, 50, 80, 95],
                "percentiles must be unique",
            ),
        ],
    )
    def test_section_filter(
        self,
        qtbot,
        model_config,
        recorder_name,
        expected_percentiles,
        validation_message,
    ):
        """
        Tests the section filter method.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value() == recorder_name
        )

        # 1. Check value
        field = form.find_field_by_name("percentiles")
        assert field.value()["values"] == expected_percentiles

        # 2. Validate form
        if validation_message is None:
            assert form.validate() == {
                "name": recorder_name,
                "type": "storagedurationcurve",
                "node": "Reservoir",
                "percentiles": [1, 30, 50, 80, 95],
            }
        else:
            QTimer.singleShot(100, close_message_box)
            form.validate()
            assert validation_message in field.message.text()
