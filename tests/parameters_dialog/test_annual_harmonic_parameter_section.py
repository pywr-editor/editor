import pytest
from PySide6.QtCore import QTimer

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page import ParameterPage
from pywr_editor.model import ModelConfig
from tests.utils import close_message_box, resolve_model_path


class TestDialogParameterControlCurveParameterSection:
    """
    Tests the section for AnnualHarmonicSeriesParameter.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_annual_harmonic_parameter_section.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, field_to_check, init_message, validation_message",
        [
            ("valid_harmonic", "amplitudes_phases", None, None),
            ("invalid_mean", "mean", None, "cannot be empty"),
            (
                "invalid_phases",
                "amplitudes_phases",
                "Some values were set to zero",
                None,
            ),
            (
                "invalid_amplitudes",
                "amplitudes_phases",
                "Some values were set to zero",
                None,
            ),
            (
                "invalid_harmonic_no_values",
                "amplitudes_phases",
                None,
                "provide at least 1 value",
            ),
            (
                "invalid_phase_upper_bounds",
                "phase_upper_bounds",
                "value is above the allowed maximum",
                "value is above the allowed maximum",
            ),
        ],
    )
    def test_validation(
        self,
        qtbot,
        model_config,
        param_name,
        field_to_check,
        init_message,
        validation_message,
    ):
        """
        Tests that the values are loaded correctly.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPage = dialog.pages.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert form.find_field("name").value() == param_name

        field = form.find_field(field_to_check)

        if init_message:
            assert init_message in field.message.text()
        else:
            assert field.message.text() == ""

        # send form and verify message in fields
        if validation_message:
            QTimer.singleShot(100, close_message_box)
            form.validate()
            assert validation_message in field.message.text()
        else:
            form.validate()
            assert field.message.text() == ""
