from functools import partial

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QWidget

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page import ParameterPage
from pywr_editor.form import CheckSumWidget, FormField, ParameterForm
from pywr_editor.model import ModelConfig, ParameterConfig
from pywr_editor.widgets import PushIconButton
from tests.utils import resolve_model_path


class TestDialogParameterCheckSumWidget:
    """
    Tests the CheckSumWidget.
    """

    @staticmethod
    def widget(
        value: list[int | float] | dict | None,
    ) -> CheckSumWidget:
        """
        Initialises the form and returns the widget.
        :param value: The dictionary containing the checksum data.
        :return: An instance of CheckSumWidget.
        """
        # mock widgets
        form = ParameterForm(
            model_config=ModelConfig(resolve_model_path("model_tables.json")),
            parameter_obj=ParameterConfig({}),
            fields={
                "Section": [
                    {
                        "name": "checksum",
                        "field_type": CheckSumWidget,
                        "value": value,
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        form.enable_optimisation_section = False
        form.load_fields()

        form_field = form.find_field("checksum")
        # noinspection PyTypeChecker
        return form_field.widget

    @pytest.mark.parametrize(
        "value, expected_value",
        [
            # only first hash is returned
            (
                {
                    "md5": "a5c4032e2d8f5205ca99dedcfa4cd18e",
                    "sha256": "0f75b3cee325d37112687d3d10596f44e0add374f4e40a1b6687912c05e65366",  # noqa: E501
                },
                {
                    "md5": "a5c4032e2d8f5205ca99dedcfa4cd18e",
                },
            ),
            # empty value - validation passes
            ({}, {}),
        ],
    )
    def test_valid(self, qtbot, value, expected_value):
        """
        Tests that the field is loaded correctly.
        """
        widget = self.widget(value=value)
        form_field: FormField = widget.field
        line_edit = widget.line_edit
        combo_box = widget.combo_box

        # 1. Check field
        assert form_field.message.text() == ""
        if value:
            assert combo_box.currentText() == widget.labels_map[list(value.keys())[0]]
            assert line_edit.text() == list(value.values())[0]
        else:
            assert combo_box.currentText() == "None"
            assert line_edit.text() == ""
        assert widget.get_value() == expected_value

        # 2. Validation
        out = widget.validate("", "", widget.get_value())
        assert out.validation is True

        # 4. Test reset
        widget.reset()
        assert line_edit.text() == ""
        assert combo_box.currentText() == "None"

    @pytest.mark.parametrize(
        "value, init_message, validation_message",
        [
            # missing hash
            (
                {
                    "md5": "",
                },
                "must provide the file hash",
                "must provide the hash",
            ),
            # missing algorithm name
            (
                {
                    "": "0f75b3cee325d37112687d3d10596f44e0add374f4e40a1b6687912c05e65366",  # noqa: E501
                },
                "is not a valid type",
                "must select the algorithm name",
            ),
            # empty strings
            (
                {"": ""},
                [
                    "must provide the file hash",
                    "is not a valid type",
                ],
                None,
            ),
        ],
    )
    def test_invalid(
        self,
        qtbot,
        value,
        init_message,
        validation_message,
    ):
        """
        Tests the field validation.
        """
        widget = self.widget(value=value)
        form_field: FormField = widget.field

        if init_message:
            if isinstance(init_message, str):
                assert init_message in form_field.message.text()
            elif isinstance(init_message, list):
                for message in init_message:
                    assert message in form_field.message.text()

        out = widget.validate("", "", "")
        if validation_message is None:
            assert out.validation is True
        else:
            assert out.validation is False
            assert validation_message in out.error_message

    @pytest.mark.parametrize(
        "param_name, algorithm, error_message, expected_hash",
        [
            (
                "check_sum_calc_valid",
                "md5",
                None,
                "eb0b0e23a8bb1bce2858111b9ec6dfec",
            ),
            # # algorithm not set
            # (
            #     "check_sum_calc_valid",
            #     None,
            #     "select an algorithm",
            #     None,
            # ),
            # (
            #     "check_sum_calc_no_url",
            #     "md5",
            #     "can be only calculated for an external file",
            #     None,
            # ),
            # (
            #     "check_sum_calc_non_existing_url",
            #     "md5",
            #     "field does not exist",
            #     None,
            # ),
        ],
    )
    def test_checksum_calculation(
        self, qtbot, param_name, algorithm, error_message, expected_hash
    ):
        """
        Test the checksum calculation (use the md5 algorithm).
        """
        model_config = ModelConfig(
            resolve_model_path(
                "model_dialog_parameter_tables_array_parameter_section.json"
            )
        )
        dialog = ParametersDialog(model_config, param_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: ParameterPage = dialog.pages.currentWidget()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        check_sum_field: FormField = selected_page.findChild(FormField, "checksum")
        # noinspection PyTypeChecker
        check_sum_widget: CheckSumWidget = check_sum_field.widget
        # noinspection PyTypeChecker
        button: PushIconButton = check_sum_widget.findChild(
            PushIconButton, "calculate_button"
        )

        # set algorithm to md5
        if algorithm is not None:
            check_sum_widget.combo_box.setCurrentText(
                check_sum_widget.labels_map[algorithm]
            )

        # calculate hash
        if error_message is None:
            QTimer.singleShot(100, partial(self._check_msg, qtbot))
            qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
            assert check_sum_widget.line_edit.text() == expected_hash
        # error
        else:
            QTimer.singleShot(100, partial(self._check_msg, qtbot, error_message))
            qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        assert button.isEnabled() is True
        assert button.text() == "Calculate"

    @staticmethod
    def _check_msg(qtbot, message=None):
        widget: QMessageBox = QApplication.activeModalWidget()
        if widget is not None:
            text = widget.text()
            # critical window
            if message:
                assert message in text
            # warning before calculating hash
            else:
                qtbot.mouseClick(
                    widget.findChild(QPushButton), Qt.MouseButton.LeftButton
                )
            widget.close()
        else:
            assert False
