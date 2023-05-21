import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QPushButton

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import (
    ColumnWidget,
    FormField,
    IndexColWidget,
    SheetNameWidget,
    TableSelectorWidget,
    UrlWidget,
)
from pywr_editor.model import ModelConfig
from pywr_editor.utils import get_columns, get_index_names
from tests.utils import close_message_box, resolve_model_path

"""
 Tests for ColumnWidget. The class tests the widget behaviour
 both with the UrlWidget and TableSelectorWidget. The test outcomes
 must be the same regardless of the widget used to source the DataFrame.
"""


# called once per each test function
def pytest_generate_tests(metafunc):
    func_name = metafunc.function.__name__
    if func_name not in metafunc.cls.params:
        return

    func_name = metafunc.cls.params[func_name]
    parameter_names = f"model_file, widget_name, {func_name['params']}"

    parameter_sets = []
    for widget_name, model_file in metafunc.cls.model_files.items():
        parameter_sets = parameter_sets + [
            (
                model_file,
                widget_name,
            )
            + scenario_set
            for scenario_set in func_name["scenarios"]
        ]

    metafunc.parametrize(parameter_names, parameter_sets)


class TestDialogParameterColumnWidget:
    """
    Tests the ColumnWidget in the parameter dialog. This is used for anonymous and
    non-anonymous tables.
    """

    model_files = {
        "url": "model_dialog_parameters_column_widget_w_url.json",
        "table": "model_dialog_parameters_column_widget_w_table_selector.json",
    }
    params = {
        "test_columns": {
            "params": "param_name, expected, warning_msg",
            "scenarios": [
                # column is a string
                ("param_with_column_str", "Column 3", ""),
                # column is an integer
                # column does not exist
                ("param_with_non_existing_column", None, "does not exist"),
                # column is index and therefore not available
                ("param_with_column_is_index", None, "does not exist"),
                # empty or invalid types do not show a warning message
                # column is valid but an empty string
                ("param_no_index_col", None, ""),
                # column is not provided - this is mandatory
                ("param_with_no_column", None, ""),
                # column has invalid type (list - can only be a string)
                ("param_with_invalid_column_type", None, ""),
                # column has invalid type (null)
                ("param_with_invalid_column_type2", None, ""),
            ],
        },
        "test_column_with_ints": {
            "params": "param_name",
            "scenarios": [("param_with_column_int",)],
        },
        "test_non_existing_file": {
            "params": "param_name",
            "scenarios": [("param_non_existing_file",)],
        },
        "test_h5_file": {
            "params": "param_name, expected_columns, selected",
            "scenarios": [
                (
                    "param_with_h5_table_index_col",
                    ["Column 1", "Column 3", "Column 4"],
                    "Column 3",
                )
            ],
        },
    }

    def test_columns(
        self, qtbot, model_file, widget_name, param_name, expected, warning_msg
    ):
        """
        Tests that the field loads the columns and sets the selected column using the
        UlrWidget or TableSelectorWidget.
        """
        model_config = ModelConfig(resolve_model_path(model_file))

        all_columns = {"Column 1", "Column 2", "Column 3", "Column 4"}
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.show()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        column_field: FormField = selected_page.findChild(FormField, "column")
        # noinspection PyTypeChecker
        column_widget: ColumnWidget = column_field.widget
        # noinspection PyUnresolvedReferences
        widget_with_table: UrlWidget | TableSelectorWidget = selected_page.findChild(
            FormField, widget_name
        ).widget
        spy = QSignalSpy(widget_with_table.updated_table)

        # 1. Columns are loaded without warning messages and the selected column is
        # checked
        columns = all_columns - set(get_index_names(widget_with_table.table))
        columns = ["None"] + sorted(list(columns))
        assert column_widget.combo_box.all_items == columns
        # valid
        if warning_msg == "":
            assert column_field.message.text() == warning_msg
            assert column_widget.wrong_column is False
        # invalid
        else:
            assert warning_msg in column_field.message.text()
            assert column_widget.wrong_column is True

        assert column_field.value() == expected
        assert spy.count() == 0

        # if no column is selected, None should appear in the line_edit field
        if not expected:
            assert column_widget.combo_box.currentText() == "None"

        # 2. Test field reload
        reload_button = widget_with_table.reload_button

        # warning message is removed
        qtbot.mouseClick(reload_button, Qt.MouseButton.LeftButton)
        assert spy.count() == 1
        assert column_field.message.text() == ""
        assert column_widget.combo_box.all_items == columns
        assert column_field.value() == expected

        # 3. Validation - it fails if expected value is None
        QTimer.singleShot(100, close_message_box)
        output = column_widget.validate("column", "Column", column_widget.get_value())
        if expected is None:
            assert output.validation is False
            form_data = column_widget.form.validate()
            assert form_data is False
            assert (
                column_field.message.text() == "You must select a column from the list"
            )
        else:
            assert output.validation is True
            form = column_widget.form
            form_data = form.validate()
            assert column_field.message.text() == ""

            assert isinstance(form_data, dict)
            assert form_data["name"] == param_name
            assert form_data["type"] == "constant"
            if widget_name == "url":
                assert "url" in form_data
                assert "table" not in form_data
            elif widget_name == "table":
                assert "url" not in form_data
                assert "table" in form_data
            assert "source" not in form_data
            assert form_data["column"] == column_widget.get_value()
            assert widget_name in form_data.keys()

            # 4. Save form to test filter
            # noinspection PyTypeChecker
            save_button: QPushButton = selected_page.findChild(
                QPushButton, "save_button"
            )
            # enable button (disabled due to no changes)
            assert model_config.has_changes is False
            assert save_button.isEnabled() is False
            save_button.setEnabled(True)
            qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
            assert model_config.has_changes is True

            fields = [widget_name, "index", "column"]
            model_param_dict = {"type": "constant"}
            if widget_name == "url":
                if widget_with_table.file_ext == ".csv":
                    fields += ["index_col", "parse_dates"]
                elif widget_with_table.file_ext == ".xlsx":
                    fields += ["index_col", "parse_dates", "sheet_name"]
                else:
                    fields += ["key"]
            for f in fields:
                # noinspection PyArgumentList
                value = form.find_field_by_name(f).widget.get_value()
                # convert index_col to integer
                if f == "index_col" and "xlsx" in widget_with_table.file_ext:
                    all_cols = list(widget_with_table.table.columns)
                    value = [all_cols.index(col_name) for col_name in value]

                if value:
                    model_param_dict[f] = value

            assert model_config.parameters.config(param_name) == model_param_dict

    def test_column_with_ints(self, qtbot, model_file, widget_name, param_name):
        """
        Tests when the column names are integers.
        """
        model_config = ModelConfig(resolve_model_path(model_file))

        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.show()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name
        # noinspection PyTypeChecker
        column_field: FormField = selected_page.findChild(FormField, "column")
        # noinspection PyTypeChecker
        column_widget: ColumnWidget = column_field.widget

        assert column_widget.value == 5
        assert column_widget.combo_box.currentData() == int
        assert column_widget.get_value() == 5
        assert (
            column_widget.validate("", "", column_widget.get_value()).validation is True
        )

        # set None and check type and validation
        column_widget.combo_box.setCurrentText("None")
        assert column_widget.combo_box.currentData() is None
        assert column_widget.get_value() is None

        assert (
            column_widget.validate("", "", column_widget.get_value()).validation
            is False
        )

    def test_non_existing_file(self, qtbot, model_file, widget_name, param_name):
        """
        Tests the widget when the table file does not exist and the table is not
        available. This also tests the updated_table Signal.
        """
        model_config = ModelConfig(resolve_model_path(model_file))

        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name
        # noinspection PyTypeChecker
        column_field: FormField = selected_page.findChild(FormField, "column")
        # noinspection PyTypeChecker
        column_widget: ColumnWidget = column_field.widget
        # noinspection PyUnresolvedReferences
        widget_with_table: UrlWidget | TableSelectorWidget = selected_page.findChild(
            FormField, widget_name
        ).widget
        spy_updated_table = QSignalSpy(widget_with_table.updated_table)

        # 1. Check field is disabled
        assert widget_with_table.table is None
        assert column_widget.combo_box.isEnabled() is False
        # no message is set on the field (just the url field)
        assert column_field.message.text() == ""
        # value are not changed - in case file is fixed in url field
        assert column_widget.value == " Date"
        assert column_field.value() is None
        assert spy_updated_table.count() == 0

        # field contains "None"
        assert column_widget.combo_box.currentText() == "None"

        # 2. Test field reload
        reload_button = widget_with_table.reload_button
        assert reload_button.isEnabled() is True
        qtbot.mouseClick(reload_button, Qt.MouseButton.LeftButton)
        assert spy_updated_table.count() == 1
        assert column_widget.combo_box.isEnabled() is False
        assert column_field.value() is None

        QTimer.singleShot(100, close_message_box)
        output = column_widget.validate("column", "Column", column_widget.get_value())
        assert output.validation is False
        form_data = column_widget.form.validate()
        assert form_data is False
        assert column_field.message.text() == "You must select a column from the list"

        # 3. Trigger emission of updated_table Signal by changing file or table
        expected_column = " Date"
        if widget_name == "url":
            # Change file to existing one
            widget_with_table.line_edit.setText("files/table.csv")
        elif widget_name == "table":
            # Change the selected table
            widget_with_table.combo_box.setCurrentText("csv_table")

        assert widget_with_table.table is not None
        assert spy_updated_table.count() == 2

        # field is enabled and updated
        assert column_widget.combo_box.isEnabled() is True
        assert column_widget.combo_box.all_items == [  # index are removed
            "None",
            " Date",
            "Column 3",
        ]
        # value is updated with correct column
        assert column_widget.value == expected_column
        assert column_field.value() == expected_column

        # 4. Test field reload again
        qtbot.mouseClick(reload_button, Qt.MouseButton.LeftButton)
        assert spy_updated_table.count() == 3
        assert column_widget.combo_box.isEnabled() is True
        assert column_field.value() == expected_column

        # 5. Set now non-existing file
        if widget_name == "url":
            # Change file to non-existing one
            widget_with_table.line_edit.setText("files/table__.csv")
            # table is not available
            assert widget_with_table.table is None
            assert spy_updated_table.count() == 4

            # field is disabled and empty
            # assert column_field.message.text() == "" error from validation
            assert column_widget.combo_box.isEnabled() is False
            assert column_widget.combo_box.all_items == ["None"]
            # value is updated with correct column
            assert column_widget.value == expected_column
            # table is not available, field returns None
            assert column_field.value() is None

    def test_table_reload(self, qtbot):
        """
        Tests the table_update Signal, for example when the sheet name is changed.
        This applies only to UrlWidget and anonymous tables. With TableSelectorWidget
        the only way to reload a table is via the Refresh button - table parsing
        options cannot be changed.
        """
        model_config = ModelConfig(resolve_model_path(self.model_files["url"]))

        param_name = "param_empty_sheet"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name
        # noinspection PyTypeChecker
        column_field: FormField = selected_page.findChild(FormField, "column")
        # noinspection PyTypeChecker
        column_widget: ColumnWidget = column_field.widget
        # noinspection PyUnresolvedReferences
        sheet_widget: SheetNameWidget = selected_page.findChild(
            FormField, "sheet_name"
        ).widget
        # noinspection PyUnresolvedReferences
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget
        spy = QSignalSpy(url_widget.updated_table)

        # 1. Change the sheet to reload the table
        assert spy.count() == 0
        sheet_widget.combo_box.setCurrentText("Sheet 1")
        assert spy.count() == 1
        assert column_widget.combo_box.all_items == [
            "None",
            "Column 1",
            "Column 2",
        ]
        # 2. previously selected columns are checked
        expected = "Column 2"
        assert column_widget.wrong_column is False
        assert column_field.value() == expected

    @pytest.mark.parametrize(
        "new_index, warning_msg",
        [
            (["Column 1"], ""),
            (["Column 1", "Column 2"], ""),
            (["Column 3"], "does not exist"),
        ],
    )
    def test_index_changed_signal(self, qtbot, new_index, warning_msg):
        """
        Checks that, when the DataFrame index is changed via IndexColWidget, the
        columns list is updated. This only applies to anonymous tables (with UrlWidget).
        """
        model_config = ModelConfig(resolve_model_path(self.model_files["url"]))

        param_name = "param_with_column_str"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        column_field: FormField = selected_page.findChild(FormField, "column")
        column_widget: ColumnWidget = column_field.widget

        index_col_widget: IndexColWidget = selected_page.findChild(
            FormField, "index_col"
        ).widget
        index_col_combo_box = index_col_widget.combo_box
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget
        spy_updated_table = QSignalSpy(url_widget.updated_table)
        spy_index_changed = QSignalSpy(url_widget.index_changed)

        # 1. Change the index
        # Slot is triggered every time a new item is checked
        selected_indexes = [
            index_col_combo_box.all_items.index(col_name) for col_name in new_index
        ]
        # de-select all
        index_col_combo_box.uncheck_all()
        # only the index_changed Signal is emitted
        assert spy_updated_table.count() == 0
        assert spy_index_changed.count() == 1

        # select only some columns
        index_col_combo_box.check_items(selected_indexes)

        # 2. The columns are updated in the widget
        columns = get_columns(url_widget.table)
        assert column_widget.combo_box.all_items == ["None"] + columns

        # check selection
        if warning_msg == "":
            assert column_field.message.text() == ""
            assert column_widget.get_value() == "Column 3"
        # warning appears when index is the selected column (column is not found)
        else:
            assert warning_msg in column_field.message.text()
            assert column_widget.get_value() is None

    @pytest.mark.parametrize(
        "param_name, valid",
        [
            ("param_with_column_str", True),
            ("param_with_non_existing_column", False),
        ],
    )
    def test_change_value(self, qtbot, param_name, valid):
        """
        Checks that, when the user changes the selected column, the internal value is
        updated. This test does not depend on any table source widget.
        """
        model_config = ModelConfig(resolve_model_path(self.model_files["url"]))

        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        column_field: FormField = selected_page.findChild(FormField, "column")
        # noinspection PyTypeChecker
        column_widget: ColumnWidget = column_field.widget
        # noinspection PyUnresolvedReferences
        spy = QSignalSpy(column_widget.combo_box.currentTextChanged)

        if valid is False:
            assert column_field.message.text() != ""

        new_selection = "Column 4"
        assert spy.count() == 0
        column_widget.combo_box.setCurrentText(new_selection)
        assert spy.count() == 1
        assert column_widget.get_value() == new_selection
        assert column_widget.value == new_selection

        # if the value was valid the previously set warning message is removed
        if valid is False:
            assert column_field.message.text() == ""

    def test_table_wo_columns(self, qtbot):
        """
        Tests that a warning message is shown, if the table does not contain any
        column. This test does not depend on any table source widget.
        """
        model_config = ModelConfig(resolve_model_path(self.model_files["url"]))

        param_name = "param_empty_sheet"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name
        # noinspection PyTypeChecker
        column_field: FormField = selected_page.findChild(FormField, "column")
        # noinspection PyTypeChecker
        column_widget: ColumnWidget = column_field.widget

        assert column_field.message.text() == "The table does not contain any column"
        assert column_widget.combo_box.all_items == ["None"]
        assert column_widget.get_value() is None

        QTimer.singleShot(100, close_message_box)
        output = column_widget.validate("column", "Column", column_widget.get_value())
        assert output.validation is False
        form_data = column_widget.form.validate()
        assert form_data is False
        assert column_field.message.text() == "You must select a column from the list"

    def test_h5_file(
        self,
        qtbot,
        model_file,
        widget_name,
        param_name,
        expected_columns,
        selected,
    ):
        """
        Tests the widget with H5 files.
        """
        model_config = ModelConfig(resolve_model_path(model_file))

        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.show()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name
        # noinspection PyTypeChecker
        column_field: FormField = selected_page.findChild(FormField, "column")
        # noinspection PyTypeChecker
        column_widget: ColumnWidget = column_field.widget
        form = column_widget.form

        # 1. Check field
        assert column_widget.combo_box.all_items == ["None"] + expected_columns
        assert column_widget.get_value() == selected

        # 2. Validate
        output = column_widget.validate("column", "Column", column_widget.get_value())
        assert output.validation is True
        form_data = form.validate()

        assert column_field.message.text() == ""

        assert isinstance(form_data, dict)
        assert form_data["name"] == param_name
        assert form_data["type"] == "constant"
        if widget_name == "url":
            assert "url" in form_data
            assert "table" not in form_data
        elif widget_name == "table":
            assert "url" not in form_data
            assert "table" in form_data
        assert "source" not in form_data
        assert form_data["column"] == column_widget.get_value()
        assert widget_name in form_data.keys()

        # 3. Save form to test filter
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(QPushButton, "save_button")
        # enable button (disabled due to no changes)
        assert model_config.has_changes is False
        assert save_button.isEnabled() is False
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert model_config.has_changes is True

        fields = [widget_name, "index", "column", "key"]
        model_param_dict = {"type": "constant"}
        for f in fields:
            # noinspection PyArgumentList
            value = form.find_field_by_name(f).widget.get_value()
            if value:
                model_param_dict[f] = value
        assert model_config.parameters.config(param_name) == model_param_dict

    def test_optional_arg(self, qtbot):
        """
        Tests field validation when the field is optional.
        """
        model_config = ModelConfig(resolve_model_path(self.model_files["url"]))

        param_name = "param_with_column_str"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        column_field: FormField = selected_page.findChild(FormField, "column")
        # noinspection PyTypeChecker
        column_widget: ColumnWidget = column_field.widget
        # mock option
        column_widget.optional = True

        column_widget.combo_box.setCurrentText("None")
        out = column_widget.validate("", "", column_widget.get_value())
        assert out.validation is True
