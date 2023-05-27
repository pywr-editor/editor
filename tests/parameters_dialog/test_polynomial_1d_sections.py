from functools import partial

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QPushButton

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page_widget import ParameterPageWidget
from pywr_editor.form import (
    BooleanWidget,
    FormField,
    NodePickerWidget,
    ParameterLineEditWidget,
    StoragePickerWidget,
)
from pywr_editor.model import ModelConfig, ParameterConfig
from tests.utils import check_msg, resolve_model_path


class TestDialogParameterPolynomial1DParameterSection:
    """
    Tests the sections for the Polynomial1DParameter.
    """

    model_file = resolve_model_path("model_dialog_parameter_polynomial_1d_section.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @staticmethod
    def validate(qtbot, save_button: QPushButton, message: str | None) -> None:
        """
        Validates the form and check if the message is returned by the section.
        :param qtbot: The qtbot instance.
        :param save_button: The save button instance.
        :param message: The message to check. None to skip the assertion.
        :return: None
        """
        if message is not None:
            QTimer.singleShot(
                100,
                partial(check_msg, message),
            )
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

    def test_validation(self, qtbot, model_config):
        """
        Tests that the section validation works as expected. Only one independent
        variable.
        """
        param_name = "polynomial"
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        storage: StoragePickerWidget = form.find_field("storage_node").widget
        node: NodePickerWidget = form.find_field("node").widget
        parameter: ParameterLineEditWidget = form.find_field("parameter").widget

        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")

        # 1. Save form w/o independent variable
        self.validate(qtbot, save_button, "must provide the independent variable")

        # 2. Set storage_node
        storage.combo_box.setCurrentText("Reservoir (Storage)")
        assert storage.get_value() == "Reservoir"
        self.validate(qtbot, save_button, None)

        # 3. Set storage_node and node
        node.combo_box.setCurrentText("Link (Link)")
        assert node.get_value() == "Link"
        self.validate(qtbot, save_button, "can provide only one type")

        # 4. Set all
        parameter.parameter_obj = ParameterConfig({"type": "constant", "value": 5})
        self.validate(qtbot, save_button, "can provide only one type")

        # 5. Clear parameter and storage_node
        parameter.reset()
        storage.reset()
        self.validate(qtbot, save_button, None)

        # 6. Set use_proportional_volume w/o storage node
        prop_volume: BooleanWidget = form.find_field("use_proportional_volume").widget
        prop_volume.toggle.setChecked(True)
        assert form.validate() == {
            "name": "polynomial",
            "type": "polynomial1d",
            "coefficients": [123, 67, 4e-18],
            "node": "Link",
        }
