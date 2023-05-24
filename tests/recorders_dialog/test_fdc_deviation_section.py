import pytest
from PySide6.QtCore import QTimer

from pywr_editor.dialogs import RecordersDialog
from pywr_editor.dialogs.recorders.recorder_page_widget import RecorderPageWidget
from pywr_editor.form import FormField
from pywr_editor.model import ModelConfig
from tests.utils import close_message_box, resolve_model_path


class TestDialogRecorderFlowDurationCurveDeviationRecorderSectionSection:
    """
    Tests the FlowDurationCurveDeviationRecorderSection.
    """

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(
            resolve_model_path("model_recorders_fdc_deviation_section.json")
        )

    @pytest.mark.parametrize(
        "recorder_name, expected_targets",
        [
            # targets not validated because they are empty
            ("valid_no_targets", {}),
            # upper target not provided
            (
                "valid_with_one_target",
                {"lower_target_fdc": [13, 56, 90, 101, 200]},
            ),
            # target is external file - validation is skipped
            (
                "valid_with_external_target",
                {"lower_target_fdc": {"url": "files/table.csv", "index": 0}},
            ),
        ],
    )
    def test_valid_fdc_targets(
        self,
        qtbot,
        model_config,
        recorder_name,
        expected_targets,
    ):
        """
        Tests the initialisation of the FDC targets.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == recorder_name

        # 1. Check value
        for name, expected_values in expected_targets.items():
            field = form.find_field(name)
            assert field.value() == expected_values

        # 2. Validate form
        assert form.validate() == {
            **{
                "name": recorder_name,
                "type": "flowdurationcurvedeviation",
                "node": "Reservoir",
                "percentiles": [30, 40, 50, 80, 95],
            },
            **expected_targets,
        }

    @pytest.mark.parametrize(
        "recorder_name, validation_message",
        [
            ("invalid_target_size", "must match the number of percentiles"),
        ],
    )
    def test_invalid_fdc_targets(
        self,
        qtbot,
        model_config,
        recorder_name,
        validation_message,
    ):
        """
        Tests the validation of the FDC targets.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == recorder_name

        # Validate form
        field = form.find_field("lower_target_fdc")
        QTimer.singleShot(100, close_message_box)
        form.validate()
        assert validation_message in field.message.text()
