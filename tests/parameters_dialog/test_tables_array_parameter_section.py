import pytest
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs.parameters.parameter_page_widget import (
    ParameterPageWidget,
)
from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import (
    H5FileWidget,
    H5WhereWidget,
    H5NodeWidget,
    FormField,
)
from tests.utils import resolve_model_path


class TestDialogParameterTablesArrayParameterSection:
    """
    Tests the section for TablesArrayParameter
    """

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(
            resolve_model_path(
                "model_dialog_parameter_tables_array_parameter_section.json"
            )
        )

    @pytest.mark.parametrize(
        "param_name, values, validation_messages",
        [
            (
                "valid",
                {
                    "file": "files/pytable_ts.h5",
                    "where": "/timeseries2",
                    "node": "block0_values",
                },
                {"file": None, "where": None, "node": None},
            ),
            (
                "valid_no_file",
                {"file": None, "where": None, "node": None},
                {
                    "file": "provide a valid file containing",
                    # validation on where attribute and node fields skipped
                    "where": None,
                    "node": None,
                },
            ),
            (
                "valid_no_where",
                {"file": "files/pytable_ts.h5", "where": None, "node": None},
                {"file": None, "where": "must select a name", "node": None},
            ),
            (
                "valid_no_node",
                {
                    "file": "files/pytable_ts.h5",
                    "where": "/timeseries2",
                    "node": None,
                },
                {"file": None, "where": None, "node": "must select a node"},
            ),
        ],
    )
    def test_valid(
        self, qtbot, model_config, param_name, values, validation_messages
    ):
        """
        Tests that the values are loaded correctly.
        """
        dialog = ParametersDialog(model_config, param_name)
        file = values["file"]
        where = values["where"]
        node = values["node"]

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        file_field: FormField = selected_page.findChild(FormField, "url")
        # noinspection PyTypeChecker
        file_widget: H5FileWidget = file_field.widget

        # noinspection PyTypeChecker
        where_field: FormField = selected_page.findChild(FormField, "where")
        # noinspection PyTypeChecker
        where_widget: H5WhereWidget = where_field.widget

        # noinspection PyTypeChecker
        node_field: FormField = selected_page.findChild(FormField, "node")
        # noinspection PyTypeChecker
        node_widget: H5NodeWidget = node_field.widget

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. Check message and value
        assert file_field.message.text() == ""
        assert where_field.message.text() == ""
        if file:
            assert file_widget.line_edit.text() == file
            assert file_field.value() == file
            assert where_widget.combo_box.all_items == [
                "None",
                "/inflows",
                "/timeseries2",
            ]
        else:
            assert file_widget.line_edit.text() == ""
            assert file_field.value() is None
            assert where_widget.combo_box.all_items == ["None"]

        if where:
            assert where_widget.combo_box.currentText() == where
            assert where_widget.combo_box.isEnabled() is True
            assert where_widget.node_keys == [
                "axis0",
                "axis1",
                "block0_items",
                "block0_values",
            ]
            assert where_field.value() == where
        else:
            assert where_widget.combo_box.currentText() == "None"
            assert where_widget.combo_box.isEnabled() is (
                param_name != "valid_no_file"
            )
            assert where_field.value() is None

        if node:
            assert node_widget.combo_box.currentText() == node
            assert node_widget.combo_box.isEnabled() is True
            assert node_widget.combo_box.all_items == [
                "None",
                "axis0",
                "axis1",
                "block0_items",
                "block0_values",
            ]
            assert node_field.value() == node
        else:
            assert node_widget.combo_box.currentText() == "None"
            # when file is NA or where attribute is not selected, field is disabled
            assert node_widget.combo_box.isEnabled() is (
                param_name not in ["valid_no_file", "valid_no_where"]
            )
            assert node_field.value() is None

        # 2. Validate
        data = {"file": file_widget, "where": where_widget, "node": node_widget}
        for message_key, widget in data.items():
            out = widget.validate("", "", "")
            message: str | None = validation_messages[message_key]

            if message is None:
                assert out.validation is True
            else:
                assert out.validation is False
                assert message in out.error_message

        # 3. Reload
        spy = QSignalSpy(file_widget.file_changed)
        qtbot.mouseClick(file_widget.reload_button, Qt.MouseButton.LeftButton)
        assert spy.count() == 1

        assert file_field.message.text() == ""
        if file:
            assert file_widget.line_edit.text() == file
            assert file_field.value() == file
        else:
            assert file_widget.line_edit.text() == ""
            assert file_field.value() is None

        # 4. Reset
        file_widget.reset()
        assert file_field.message.text() == ""
        assert file_widget.line_edit.text() == ""
        assert file_field.value() is None
        assert file_widget.keys == {}

        assert where_widget.combo_box.isEnabled() is False
        assert where_widget.node_keys == []

        assert node_widget.combo_box.isEnabled() is False

    @pytest.mark.parametrize(
        "param_name, field, init_message, validation_message",
        [
            # wrong extension
            (
                "invalid_extension",
                "url",
                "file extension must be .h5",
                "provide a valid file containing",
            ),
            # non-existing h5 file
            (
                "invalid_non_existing",
                "url",
                "does not exist",
                "provide a valid file containing",
            ),
            # non-existing where attribute
            (
                "invalid_non_existing_where",
                "where",
                "does not exist",
                "must select a name",
            ),
            # wrong where type (list)
            (
                "invalid_wrong_where_type",
                "where",
                "is not a valid type",
                "must select a name",
            ),
            # non-existing where attribute
            (
                "invalid_non_existing_node",
                "node",
                "does not exist",
                "must select a node",
            ),
        ],
    )
    def test_invalid(
        self,
        qtbot,
        model_config,
        param_name,
        field,
        init_message,
        validation_message,
    ):
        """
        Tests the fields when invalid data are given.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        form_field: FormField = selected_page.findChild(FormField, field)
        # noinspection PyTypeChecker
        widget: H5FileWidget | H5WhereWidget = form_field.widget

        # 1. Test value and init message
        assert init_message in form_field.message.text()
        if field == "url":
            assert form_field.value() is not None
            assert widget.keys == {}
        else:
            assert form_field.value() is None
            assert widget.combo_box.currentText() == "None"
            assert widget.combo_box.isEnabled() is True

        # 2. Test validation message
        out = widget.validate("", "", "")
        assert validation_message in out.error_message

        # 3. Reload
        if field == "url":
            spy = QSignalSpy(widget.file_changed)
            qtbot.mouseClick(widget.reload_button, Qt.MouseButton.LeftButton)
            assert spy.count() == 1

            assert init_message in form_field.message.text()
            assert form_field.value() is not None
            assert widget.keys == {}

            # 4. Reset
            widget.reset()
            assert form_field.message.text() == ""
            assert widget.line_edit.text() == ""
            assert form_field.value() is None
            assert widget.keys == {}

    def test_file_change(self, qtbot, model_config):
        """
        Tests on_update_file and normalise for H5FileWidget, and on_update_file
        # and populate_widget for H5WhereWidget
        """
        param_name = "valid"
        file = "files/pytable_ts.h5"
        dialog = ParametersDialog(model_config, param_name)

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        file_field: FormField = selected_page.findChild(FormField, "url")
        # noinspection PyTypeChecker
        file_widget: H5FileWidget = file_field.widget

        # noinspection PyTypeChecker
        where_field: FormField = selected_page.findChild(FormField, "where")
        # noinspection PyTypeChecker
        where_widget: H5WhereWidget = where_field.widget

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        spy = QSignalSpy(file_widget.file_changed)

        # change the values
        new_file_values = {
            # remove extension
            file[:-1]: "file extension must be .h5",
            # non-existing h5 file
            "files/non-existing.h5": "does not exist",
            # absolute path convert to relative but with dots
            str(
                Path(__file__).parent.parent / "file_outside_path.h5"
            ): "place the table file in the",
        }

        spy_count = 1
        for new_file, file_message in new_file_values.items():
            file_widget.line_edit.setText(new_file)

            # Signal is triggered at every file change
            assert spy.count() == spy_count

            assert file_message in file_field.message.text()
            if "always recommended " not in file_field.message.text():
                # file
                assert file_widget.keys == {}
                assert file_widget.get_value() == new_file
                # where
                assert where_field.message.text() == ""
                assert where_widget.combo_box.isEnabled() is False
                assert where_widget.combo_box.currentText() == "None"
            else:
                # file
                assert file_widget.get_value() == "..\\file_outside_path.h5"
                # where
                assert where_field.message.text() == ""
                assert where_widget.combo_box.isEnabled() is True
                # when file is changed, the ComboBox value is reset to "None"
                assert where_widget.combo_box.currentText() == "None"

            spy_count += 1

    @pytest.mark.parametrize("scenario", ["empty_file", "change_where_attr"])
    def test_where_attr_change(self, qtbot, model_config, scenario):
        """
        Tests on_attribute_change in H5WhereWidget, and on_update_where in
        H5NodeWidget.
        """
        param_name = "valid"
        dialog = ParametersDialog(model_config, param_name)

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        file_field: FormField = selected_page.findChild(FormField, "url")
        # noinspection PyTypeChecker
        file_widget: H5FileWidget = file_field.widget

        # noinspection PyTypeChecker
        where_field: FormField = selected_page.findChild(FormField, "where")
        # noinspection PyTypeChecker
        where_widget: H5WhereWidget = where_field.widget

        # noinspection PyTypeChecker
        node_field: FormField = selected_page.findChild(FormField, "node")
        # noinspection PyTypeChecker
        node_widget: H5NodeWidget = node_field.widget

        # remove file
        if scenario == "empty_file":
            file_widget.line_edit.setText("")
            assert node_widget.combo_box.isEnabled() is False
            assert node_field.value() is None
            assert where_widget.node_keys == []

        # change attribute to reload nodes
        elif scenario == "change_where_attr":
            # noinspection PyUnresolvedReferences
            spy_where = QSignalSpy(where_widget.where_attr_changed)
            # noinspection PyUnresolvedReferences
            spy_node = QSignalSpy(node_widget.combo_box.currentTextChanged)

            # by changing the where attribute, the nodes are reloaded
            where_widget.combo_box.setCurrentText("None")
            assert spy_where.count() == 1
            # init, reset and set None
            assert spy_node.count() == 3
            assert where_widget.node_keys == []
            assert node_widget.combo_box.all_items == ["None"]
            assert node_widget.combo_box.isEnabled() is False
