import pytest
from PySide6.QtCore import QTimer
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import RecordersDialog
from pywr_editor.dialogs.recorders.recorder_page_widget import (
    RecorderPageWidget,
)
from pywr_editor.form import (
    FormField,
    ResampleAggFrequencyWidget,
    ResampleAggFunctionWidget,
)
from tests.utils import resolve_model_path, close_message_box


class TestDialogRecorderKDESection:
    """
    Tests the section handling KDE recorders, and the ResampleAggFrequencyWidget
    and ResampleAggFrequencyWidget.
    """

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(
            resolve_model_path("model_dialog_recorders_kde_section.json")
        )

    @pytest.mark.parametrize(
        "recorder_name, expected_freq, expected_func",
        [
            # resampling fields are both provided
            ("valid_kde", "Y", "sum"),
            # A replaced with Y
            ("valid_kde_str_replaced", "Y", "sum"),
            # not provided
            ("valid_kde_empty", None, None),
        ],
    )
    def test_valid(
        self, qtbot, model_config, recorder_name, expected_freq, expected_func
    ):
        """
        Tests the widgets' values.
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
        freq_widget: ResampleAggFrequencyWidget = form.find_field_by_name(
            "resample_freq"
        ).widget
        func_widget: ResampleAggFunctionWidget = form.find_field_by_name(
            "resample_func"
        ).widget
        assert freq_widget.get_value() == expected_freq
        assert func_widget.get_value() == expected_func

        if recorder_name == "valid_kde_empty":
            assert freq_widget.combo_box.currentText() == "Disabled"
            assert func_widget.combo_box.currentText() == "Disabled"

        # 2. Validate form
        assert form.validate() is not False

    @pytest.mark.parametrize(
        "recorder_name, field_to_check, error_message",
        [
            # missing "resample_func" field
            (
                "invalid_kde_missing_func",
                "resample_func",
                "must provided a value when you set the 'Aggregating frequency' "
                + "field above",
            ),
            # missing "resample_freq" field
            (
                "invalid_kde_missing_freq",
                "resample_freq",
                "must provided a value when you set the 'Aggregating function' "
                + "field below",
            ),
            # target_volume_pc is missing
            (
                "invalid_kde_missing_volume_pc",
                "target_volume_pc",
                "field cannot be empty",
            ),
            # target_volume_pc must be in correct range
            (
                "invalid_kde_wrong_volume_pc",
                "target_volume_pc",
                "must be a number between 0 and 1",
            ),
        ],
    )
    def test_invalid(
        self, qtbot, model_config, recorder_name, field_to_check, error_message
    ):
        """
        Tests the form validation.
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

        # validate form
        QTimer.singleShot(100, close_message_box)
        form.validate()
        field = form.find_field_by_name(field_to_check)
        assert error_message in field.message.text()
