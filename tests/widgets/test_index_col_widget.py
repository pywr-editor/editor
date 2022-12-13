import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QPushButton
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import (
    IndexColWidget,
    SheetNameWidget,
    UrlWidget,
    FormField,
)
from pywr_editor.utils import get_index_names, default_index_name
from tests.utils import resolve_model_path


class TestDialogParameterIndexColWidget:
    """
    Tests the IndexCol widget in the parameter dialog. This is only used for
    anonymous tables
    """

    model_file = resolve_model_path(
        "model_dialog_parameters_index_col_widget.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, expected",
        [
            # index_col is a string
            ("param_with_index_col_str", ["Column 2"]),
            # index_col is an integer
            ("param_with_index_col_int", ["Column 2"]),
            # index_col is a list of strings
            ("param_with_index_col_list_of_str", ["Column 1", "Column 4"]),
            # same as above but columns are not sorted
            (
                "param_with_index_col_list_of_str_unsorted",
                ["Column 1", "Column 3"],
            ),
            # index_col is a list of integers
            ("param_with_index_col_list_of_int", ["Column 2", "Column 4"]),
            # same as above but columns are not sorted
            (
                "param_with_index_col_list_of_int_unsorted",
                ["Column 2", "Column 4"],
            ),
            # index_col is valid but an empty string
            ("param_with_empty_list_index_col", []),
            # index_col is not provided
            ("param_with_anonymous_index", []),
            # test H5, index is built-in (cannot be specified with index_col)
            ("param_with_h5_table_index", ["Column 2"]),
            # test H5, index_col is passed, but it must be ignored by the widget
            ("param_with_h5_table_index_col", ["Column 2"]),
            # test H5 with anonymous index
            ("param_with_h5_table_ano_index", []),
        ],
    )
    def test_valid_col_index(self, qtbot, model_config, param_name, expected):
        """
        Tests that the field loads the columns and sets the column properly.
        """
        all_columns = [
            "Column 1",
            "Column 2",
            "Column 3",
            "Column 4",
        ]
        # different sorting for H5 with index (index always comes first)
        if param_name in [
            "param_with_h5_table_index",
            "param_with_h5_table_index_col",
        ]:
            c0 = all_columns[0]
            all_columns[0] = all_columns[1]
            all_columns[1] = c0

        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name

        index_col_field: FormField = selected_page.findChild(
            FormField, "index_col"
        )
        # noinspection PyTypeChecker
        index_col_widget: IndexColWidget = index_col_field.widget
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget
        form = url_widget.form

        # 1. Columns are loaded without warning messages
        assert index_col_widget.combo_box.all_items == all_columns
        assert index_col_field.message.text() == ""

        # 2. Selected columns are checked and index is set on the table
        assert index_col_widget.get_value() == expected

        # when index is not set, method returns default index name
        if not expected:
            assert get_index_names(url_widget.table) == [default_index_name]
        else:
            assert get_index_names(url_widget.table) == expected

        # if no column is selected, None should appear in the line_edit field
        if not expected:
            assert index_col_widget.combo_box.lineEdit().text() == "None"

        # 3. Test field reload
        spy_table = QSignalSpy(url_widget.updated_table)
        spy_index = QSignalSpy(url_widget.index_changed)
        reload_button = url_widget.reload_button

        # field is properly reloaded
        qtbot.mouseClick(reload_button, Qt.MouseButton.LeftButton)
        assert index_col_field.message.text() == ""
        assert index_col_widget.combo_box.all_items == all_columns
        assert index_col_field.value() == expected
        # check that Signals are emitted
        assert spy_table.count() == 1
        # index is not updated
        assert spy_index.count() == 0

        # 4. Test form validation
        output = index_col_widget.validate(
            "index_col", "Index", index_col_widget.get_value()
        )
        assert output.validation is True
        assert index_col_field.message.text() == ""

        form_data = form.validate()
        assert isinstance(form_data, dict)

        # 5. Save form to test filter
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        # enable button (disabled due to no changes)
        assert model_config.has_changes is False
        assert save_button.isEnabled() is False
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert model_config.has_changes is True

        fields = ["url", "index", "column"]
        model_param_dict = {"type": "constant"}
        if url_widget.file_ext == ".csv":
            fields += ["index_col", "parse_dates"]
        elif url_widget.file_ext == ".xlsx":
            fields += ["index_col", "parse_dates", "sheet_name"]
        else:
            fields += ["key"]
        for f in fields:
            value = form.find_field_by_name(f).widget.get_value()
            if value or value == 0:
                model_param_dict[f] = value

        assert (
            model_config.parameters.get_config_from_name(param_name)
            == model_param_dict
        )

    @pytest.mark.parametrize(
        "param_name, checked, invalid",
        [
            # index_col is an invalid string
            ("param_with_invalid_index_col_str", [], ["Non existing column"]),
            # index_col is an invalid integer
            ("param_with_invalid_index_col_int", [], ["6"]),
            # index_col is a list of strings with some invalid columns
            (
                "param_with_invalid_index_col_list_of_str",
                ["Column 1", "Column 3"],
                ["Non existing column"],
            ),
            # index_col is a list of integers with some invalid columns
            (
                "param_with_invalid_index_col_list_of_int",
                ["Column 1", "Column 2", "Column 4"],
                ["8"],
            ),
        ],
    )
    def test_invalid_col_index(
        self, qtbot, model_config, param_name, checked, invalid
    ):
        """
        Tests that the field when the provided column index is invalid
        """
        all_columns = [
            "Column 1",
            "Column 2",
            "Column 3",
            "Column 4",
        ]
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name

        index_col_field: FormField = selected_page.findChild(
            FormField, "index_col"
        )
        # noinspection PyTypeChecker
        index_col_widget: IndexColWidget = index_col_field.widget
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget

        # 1. Columns are loaded with a warning message because of an invalid column
        # name to use as index
        assert index_col_widget.combo_box.all_items == all_columns
        assert (
            "The following columns, currently" in index_col_field.message.text()
        )

        # 2. Only valid columns are checked
        assert index_col_field.value() == checked
        assert index_col_widget.get_value() == checked
        if not checked:
            assert get_index_names(url_widget.table) == [default_index_name]
        else:
            assert get_index_names(url_widget.table) == checked

        # if no column is selected, None should appear in the line_edit field
        if not checked:
            assert index_col_widget.combo_box.lineEdit().text() == "None"

        # 3. Check wrong columns
        assert index_col_widget.wrong_columns == invalid

        # 4. Test field reload
        spy_table = QSignalSpy(url_widget.updated_table)
        spy_index = QSignalSpy(url_widget.index_changed)
        reload_button = url_widget.reload_button

        # warning message is removed
        qtbot.mouseClick(reload_button, Qt.MouseButton.LeftButton)
        assert index_col_field.message.text() == ""
        assert index_col_widget.combo_box.all_items == all_columns
        assert sorted(index_col_field.value()) == checked
        # check that Signals are emitted
        assert spy_table.count() == 1
        assert spy_index.count() == 0

    def test_index_col_empty_table(self, qtbot, model_config):
        """
        Tests the field when an Excel sheet is provided with no content.
        """
        param_name = "param_empty_sheet"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()

        assert selected_page.findChild(FormField, "name").value() == param_name

        index_col_field: FormField = selected_page.findChild(
            FormField, "index_col"
        )
        # noinspection PyTypeChecker
        index_col_widget: IndexColWidget = index_col_field.widget

        # 1. Field is disabled with warning message
        assert index_col_widget.isEnabled() is False
        assert (
            index_col_field.message.text()
            == "The table does not contain any column"
        )
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget

        # columns are preserved internally
        assert index_col_widget.value == [0, 1]
        # form returns empty columns because table is empty
        assert index_col_field.value() == []
        assert get_index_names(url_widget.table) == [default_index_name]

        # 2. Test field reload
        reload_button = url_widget.reload_button

        # warning message is not removed and field is still disabled
        for _ in [0, 1]:
            qtbot.mouseClick(reload_button, Qt.MouseButton.LeftButton)
            assert index_col_widget.isEnabled() is False
            assert index_col_field.value() == []
            assert get_index_names(url_widget.table) == [default_index_name]

            # field is hidden by UrlWidget
            assert index_col_widget.isVisible() is False
            qtbot.wait(400)

    def test_non_existing_file(self, qtbot, model_config):
        """
        Tests the widget when the table file does not exist and the table is not
        available.
        """
        param_name = "param_non_existing_file"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        # dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name
        index_col_field: FormField = selected_page.findChild(
            FormField, "index_col"
        )
        # noinspection PyTypeChecker
        index_col_widget: IndexColWidget = index_col_field.widget
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget

        # 1. Check field is disabled
        assert index_col_widget.isEnabled() is False
        # no message is set on the field (just the url field)
        assert index_col_field.message.text() == ""
        # value are not changed - in case file is fixed in url field
        assert index_col_widget.value == [0, 1]
        assert index_col_field.value() == []

        # field is hidden by UrlWidget
        assert index_col_widget.isVisible() is False

        # 2. Test field reload
        reload_button = url_widget.reload_button
        qtbot.mouseClick(reload_button, Qt.MouseButton.LeftButton)
        assert index_col_widget.isEnabled() is False
        assert index_col_field.value() == []

        # 3. Change file to existing one
        expected = ["Column 1", "Demand centre"]
        url_widget.line_edit.setText("files/table.csv")
        # field is enabled and updated
        assert index_col_widget.isEnabled() is True
        assert index_col_widget.combo_box.all_items == [
            "Column 1",
            "Demand centre",
            "Column 3",
            " Date",
        ]

        # value is updated with previously set columns
        assert index_col_widget.value == expected
        assert index_col_field.value() == expected
        assert get_index_names(url_widget.table) == expected

        # 4. Test field reload again
        qtbot.mouseClick(reload_button, Qt.MouseButton.LeftButton)
        assert index_col_widget.isEnabled() is True
        assert index_col_field.value() == expected
        assert get_index_names(url_widget.table) == expected

    def test_table_reload(self, qtbot, model_config):
        """
        Tests the table update Signal, for example when the sheet name is changed.
        """
        param_name = "param_empty_sheet"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name
        index_col_field: FormField = selected_page.findChild(
            FormField, "index_col"
        )
        # noinspection PyTypeChecker
        index_col_widget: IndexColWidget = index_col_field.widget
        sheet_widget: SheetNameWidget = selected_page.findChild(
            FormField, "sheet_name"
        ).widget
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget

        # change the sheet to reload the table
        spy_table = QSignalSpy(url_widget.updated_table)
        spy_index = QSignalSpy(url_widget.index_changed)

        sheet_widget.combo_box.setCurrentText("Sheet 1")
        assert index_col_widget.combo_box.all_items == [
            "Column 1",
            "Column 2",
            "Column 3",
            "Column 4",
        ]
        # previously selected columns are checked
        expected = [
            "Column 1",
            "Column 2",
        ]
        assert index_col_widget.wrong_columns == []
        assert index_col_field.value() == expected
        assert get_index_names(url_widget.table) == expected

        # check that Signals are emitted
        assert spy_table.count() == 1
        assert spy_index.count() == 0

    def test_col_index_change(self, qtbot, model_config):
        """
        Tests that, when the column to use as index are changed, the field correctly
        updates the DataFrame.
        """
        param_name = "param_with_index_col_list_of_str"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()

        index_col_widget: IndexColWidget = selected_page.findChild(
            FormField, "index_col"
        ).widget
        combo_box = index_col_widget.combo_box
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget

        assert selected_page.findChild(FormField, "name").value() == param_name
        spy_table = QSignalSpy(url_widget.updated_table)
        spy_index = QSignalSpy(url_widget.index_changed)

        # 1. De-select all the columns
        # widget updates via dataChanged in model when user clicks on a checkbox.
        # Mock this.
        combo_box.uncheck_all()
        # Signal is emitted only once when index_col changes
        assert spy_index.count() == 1
        # table Signal is not emitted
        assert spy_table.count() == 0

        # check ComboBox values
        assert combo_box.checked_items() == []
        assert index_col_widget.get_value() == []
        assert get_index_names(url_widget.table) == [default_index_name]
        assert index_col_widget.combo_box.lineEdit().text() == "None"

        # 2. Select new columns
        # Slot is triggered every time a new itme is checked
        selected = ["Column 1", "Column 2"]
        selected_indexes = [
            combo_box.all_items.index(col_name) for col_name in selected
        ]

        # select only some columns
        combo_box.check_items(selected_indexes)
        # check Signal (cumulate emissions)
        assert spy_index.count() == 2
        assert spy_table.count() == 0

        # check selection
        assert combo_box.checked_items() == selected
        assert index_col_widget.get_value() == selected
        assert index_col_widget.combo_box.lineEdit().text() == ", ".join(
            selected
        )
        assert get_index_names(url_widget.table) == selected
