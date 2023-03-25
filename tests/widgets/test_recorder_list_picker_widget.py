import pytest
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QPushButton

from pywr_editor.dialogs import RecordersDialog
from pywr_editor.form import (
    FormField,
    ModelComponentPickerDialog,
    NodePickerWidget,
    RecorderPickerWidget,
    RecordersListPickerWidget,
    RecorderTypeSelectorWidget,
)
from pywr_editor.model import ModelConfig, RecorderConfig
from tests.utils import resolve_model_path


class TestDialogRecorderRecordersListPickerWidget:
    """
    Tests the RecordersListPickerWidget and related widgets.
    """

    model_file = resolve_model_path(
        "model_dialog_recorder_recorders_list_picker_widget.json"
    )
    general_anonymous_recorder_name = "main_recorder"
    general_anonymous_recorder_value = [
        "node",
        {"type": "NodeRecorder", "node": "Reservoir1"},
    ]

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "recorder_name, value",
        [
            (
                "valid_dicts",
                [
                    {"type": "node", "node": "Output"},
                    {"type": "node", "node": "Reservoir3"},
                ],
            ),
            # list with an existing model recorder
            (
                "valid_with_str",
                [
                    "node",
                    {"type": "node", "node": "Reservoir3"},
                ],
            ),
            # recorders key not provided
            ("valid_no_key", []),
            # thresholds key is an empty list
            ("valid_empty_list", []),
        ],
    )
    def test_valid_values(self, qtbot, model_config, recorder_name, value):
        """
        Tests that the values are loaded correctly for RecordersListPickerWidget.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value() == recorder_name
        )

        # noinspection PyTypeChecker
        field: FormField = selected_page.findChild(FormField, "recorders")
        # noinspection PyTypeChecker
        widget: RecordersListPickerWidget = field.widget

        # check model
        assert widget.model.values == value

        # check table view name
        for di, recorder_name in enumerate(value):
            idx = widget.model.index(di, 0)
            if isinstance(recorder_name, dict):
                recorder_obj = RecorderConfig(recorder_name)
                assert (
                    widget.model.data(idx, Qt.DisplayRole)
                    == recorder_obj.humanised_type
                )
            elif isinstance(recorder_name, str):
                recorder_obj = model_config.recorders.get_config_from_name(
                    recorder_name, as_dict=False
                )
                assert (
                    widget.model.data(idx, Qt.DisplayRole)
                    == f"{recorder_obj.name} ({recorder_obj.humanised_type})"
                )
            else:
                raise TypeError("Invalid type")

        # check warning and validation
        assert field.message.text() == ""

        output = widget.validate("", "", widget.get_value())
        if not value:
            assert output.validation is False
        else:
            assert output.validation is True

        # check value
        assert widget.get_value() == value

        # reset
        widget.reset()
        assert widget.get_value() == []

    @pytest.mark.parametrize(
        "recorder_name, init_message, validation_message, value",
        [
            (
                "invalid_type",
                "is not valid",
                "cannot be empty",
                [],
            ),
            (
                "invalid_type_in_list",
                "can contain only valid recorder configurations",
                "cannot be empty",
                [],
            ),
            (
                "invalid_type_in_list_number",
                "can contain only valid recorder configurations",
                "cannot be empty",
                [],
            ),
            (
                "invalid_wrong_param_dict",
                "must contain valid recorder configurations",
                "cannot be empty",
                [],
            ),
            # empty message but validation fails
            (
                "invalid_non_existing_recorder_name",
                "model recorders do not exist",
                "",
                [
                    {"type": "NodeRecorder", "node": "Reservoir2"},
                ],
            ),
        ],
    )
    def test_invalid_values(
        self,
        qtbot,
        model_config,
        recorder_name,
        init_message,
        validation_message,
        value,
    ):
        """
        Tests that the warning message is shown when the values are not valid for
        RecordersListPickerWidget.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value() == recorder_name
        )

        # noinspection PyTypeChecker
        field: FormField = selected_page.findChild(FormField, "recorders")
        # noinspection PyTypeChecker
        widget: RecordersListPickerWidget = field.widget

        # check warning and validation
        assert init_message in field.message.text()

        # check model and widget value
        assert widget.model.values == value
        assert widget.get_value() == value

        output = widget.validate("", "", widget.get_value())
        if validation_message != "":
            assert output.validation is False
            assert validation_message in output.error_message
        else:
            assert output.validation is True

    @staticmethod
    def select_row(widget: RecordersListPickerWidget, row_id: int) -> None:
        """
        Selects a row in the table.
        :param widget: The widget instance.
        :param row_id: The row number ot select.
        :return: None
        """
        widget.list.clearSelection()
        row = widget.model.index(row_id, 0)
        widget.list.selectionModel().select(row, QItemSelectionModel.Select)

    @pytest.mark.parametrize(
        "mode",
        ["add", "edit"],
    )
    def test_add_edit_child_anonymous_recorder(self, qtbot, model_config, mode):
        """
        Tests when a node recorder is added or edited in the recorder list.
        """
        dialog = RecordersDialog(
            model_config, self.general_anonymous_recorder_name
        )
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value()
            == self.general_anonymous_recorder_name
        )

        # noinspection PyTypeChecker
        recorders_field: FormField = selected_page.findChild(
            FormField, "recorders"
        )
        # noinspection PyTypeChecker
        recorders_widget: RecordersListPickerWidget = recorders_field.widget

        # 1. Open the dialog
        index = None
        if mode == "edit":
            index = 1
            self.select_row(recorders_widget, index)
            qtbot.mouseClick(
                recorders_widget.edit_button, Qt.MouseButton.LeftButton
            )
        elif mode == "add":
            qtbot.mouseClick(
                recorders_widget.add_button, Qt.MouseButton.LeftButton
            )
        else:
            raise ValueError("Mode not supported")

        # noinspection PyTypeChecker
        child_dialog: ModelComponentPickerDialog = selected_page.findChild(
            ModelComponentPickerDialog
        )
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(
            QPushButton, "save_button"
        )

        # 2. Configure a new or already existing recorde node and save the changes
        # noinspection PyTypeChecker
        type_widget: RecorderTypeSelectorWidget = child_dialog.findChild(
            RecorderTypeSelectorWidget
        )
        assert type_widget.get_value() == "node"

        new_node = "Reservoir2"
        # noinspection PyTypeChecker
        node_widget: NodePickerWidget = child_dialog.findChild(NodePickerWidget)
        node_widget.combo_box.setCurrentIndex(
            node_widget.combo_box.findData(new_node)
        )
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        # manually close the dialog
        child_dialog.close()

        # 3. Check the values
        new_value = self.general_anonymous_recorder_value.copy()
        if mode == "add":
            new_value.append({"type": "node", "node": new_node})
        else:
            new_value[index]["node"] = new_node
            new_value[index]["type"] = "node"

        assert recorders_widget.get_value() == new_value

        # 4. Save the entire form
        # noinspection PyTypeChecker
        main_save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert "Save" in main_save_button.text()

        # button in parent form is enabled as soon as the child form is saved
        assert main_save_button.isEnabled() is True
        qtbot.mouseClick(main_save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert model_config.recorders.get_config_from_name(
            self.general_anonymous_recorder_name
        ) == {
            "type": "aggregated",
            # function is mandatory and default to mean
            "recorder_agg_func": "mean",
            "recorders": new_value,
        }

    def test_edit_child_model_recorder(self, qtbot, model_config):
        """
        Tests when a different model recorder is selected in the parameter list.
        """
        recorder_name = "valid_with_str"
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value() == recorder_name
        )

        # noinspection PyTypeChecker
        recorders_field: FormField = selected_page.findChild(
            FormField, "recorders"
        )
        # noinspection PyTypeChecker
        recorders_widget: RecordersListPickerWidget = recorders_field.widget

        # 1. Open the dialog
        index = 0
        self.select_row(recorders_widget, index)
        qtbot.mouseClick(
            recorders_widget.edit_button, Qt.MouseButton.LeftButton
        )

        # noinspection PyTypeChecker
        child_dialog: ModelComponentPickerDialog = selected_page.findChild(
            ModelComponentPickerDialog
        )
        # noinspection PyTypeChecker
        save_button: QPushButton = child_dialog.findChild(
            QPushButton, "save_button"
        )

        # 2. Change the recorder
        new_str = "node1"
        # noinspection PyTypeChecker
        recorder_widget: RecorderPickerWidget = child_dialog.findChild(
            RecorderPickerWidget
        )

        recorder_widget.combo_box.setCurrentText(new_str)
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        # manually close the dialog
        child_dialog.close()

        # 3. Check the values
        new_value = ["node", {"type": "node", "node": "Reservoir3"}]
        new_value[index] = new_str

        assert recorders_widget.get_value() == new_value

        # 4. Save the entire form
        # noinspection PyTypeChecker
        main_save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert "Save" in main_save_button.text()

        # button in parent form is enabled as soon as the child form is saved
        assert main_save_button.isEnabled() is True
        qtbot.mouseClick(main_save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert model_config.recorders.get_config_from_name(recorder_name) == {
            "type": "aggregated",
            "recorder_agg_func": "mean",
            "recorders": new_value,
        }
