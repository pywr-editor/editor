from typing import List
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QLabel, QPushButton
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import (
    IndexWidget,
    IndexColWidget,
    TableSelectorWidget,
    UrlWidget,
    FormField,
)
from pywr_editor.widgets import ComboBox
from pywr_editor.utils import (
    get_index_names,
    default_index_name,
    get_index_values,
)
from tests.utils import resolve_model_path, close_message_box

"""
 Tests for IndexWidget. The class tests the widget behaviour
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


class TestDialogParameterIndexWidget:
    """
    Tests the IndexWidget in the parameter dialog. This is used both for anonymous
    and non-anonymous tables.
    """

    model_files = {
        "url": "model_dialog_parameters_index_widget_w_url.json",
        "table": "model_dialog_parameters_index_widget_w_table_selector.json",
    }

    params = {
        "test_valid_index": {
            "params": "param_name, dict_values, final_values",
            "scenarios": [
                # index value is a integer
                ("param_with_index_int", {"Demand centre": 2}, 2),
                # index value is a string
                ("param_with_index_str", {"Column 1": "5"}, "5"),
                # "index_col" not provided - anonymous index
                ("param_with_anonymous_index", {"Anonymous index": 1}, 1),
                # index_col is a list of index
                (
                    "param_with_index_col_as_list_int",
                    {"Column 1": "c", "Column 3": 3},
                    # url uses sort of table (Column 1 column comes before Column 3),
                    # table uses sort in index_col (which is flipped)
                    {"url": ["c", 3], "table": [3, "c"]},
                ),
                # list of int
                (
                    "param_with_index_list_int",
                    {"Demand centre": 6, "Column 3": 7},
                    # url uses sort of table (Demand centre column comes before
                    # Column 3), table uses sort in index_col (which is flipped)
                    {"url": [6, 7], "table": [7, 6]},
                ),
                # list of mixed types
                (
                    "param_with_index_list_str",
                    {"Column 1": "c", "Demand centre": 6},
                    ["c", 6],
                ),
                # index values passed using "indexes" key instead of "index"
                (
                    "param_with_indexes_key",
                    {"Column 1": "c", "Demand centre": 6},
                    ["c", 6],
                ),
                (
                    "param_with_no_index_values",
                    {"Column 1": None, "Demand centre": None},
                    None,
                ),
                ("param_h5_file", {"Column 2": 22}, 22),
                # H5 file with index_col set (not sued) and w/o index set
                ("param_with_h5_table_index_col", {"Column 2": 10}, 10),
                # anonymous index
                ("param_with_h5_table_ano_index", {"Anonymous index": 2}, 2),
            ],
        },
        "test_partial_index_values": {
            "params": "param_name, message",
            "scenarios": [
                # there are two indexes, but only one value is provided as integer
                (
                    "param_with_invalid_index_one_value_only_int",
                    "is not valid or does not exist",
                ),
                # same as above, but as list
                (
                    "param_with_invalid_index_one_value_only_list",
                    "is not valid or does not exist",
                ),
            ],
        },
        "test_invalid_table": {
            "params": "param_name, dict_values, valid_values, message",
            "scenarios": [
                # table file does not exist
                (
                    "param_non_existing_table",
                    {"Demand centre": 6, "Column 1": "c"},
                    ["c", 6],
                    "",
                ),
                # table is empty from Excel spreadsheet
                (
                    "param_empty_table",
                    {"Demand centre": 6, "Column 1": "c"},
                    ["c", 6],
                    "does not contain any column",
                ),
                # empty H5 table - same behaviour
                (
                    "param_empty_h5_table",
                    {"Demand centre": 6},
                    6,
                    "does not contain any column",
                ),
            ],
        },
        "test_invalid_index_values": {
            "params": "param_name, dict_values, expected_types, final_values, message",
            "scenarios": [
                # empty list - no values are selected and invalid value message is shown
                (
                    "param_with_empty_list",
                    {"Demand centre": None, "Column 1": None},
                    [str, int],
                    None,
                    "does not exist in the table: Column 1, Demand centre",
                ),
                # one index with wrong value
                (
                    "param_non_existing_value",
                    {"Column 1": None},
                    [str, int],
                    None,
                    "in the table: Column 1",
                ),
                # value type is wrong (str instead of int). But because "6" exists, it
                # is cast to int
                (
                    "param_wrong_type",
                    {"Demand centre": 6, "Column 1": None},
                    [str, int],
                    None,
                    "does not exist in the table: Column 1",
                ),
                # multi-index, but only one value exists in one of the indexes
                (
                    "param_non_existing_values",
                    {"Demand centre": 6, "Column 1": None},
                    [str, int],
                    None,
                    "in the table: Column 1",
                ),
                # anonymous index with value outside range
                (
                    "param_with_wrong_anonymous_index",
                    {default_index_name: None},
                    [int],
                    None,
                    f"in the table: {default_index_name}",
                ),
            ],
        },
    }

    @staticmethod
    def get_model_config(model_file: str) -> ModelConfig:
        """
        Initialises the model configuration.
        :param model_file: The JSON file to load.
        :return: The ModelConfig instance.
        """
        return ModelConfig(resolve_model_path(model_file))

    def test_valid_index(
        self,
        qtbot,
        model_file,
        widget_name,
        param_name,
        dict_values,
        final_values,
    ):
        """
        Tests that the field sets the proper index names and loads their values.
        """
        model_config = self.get_model_config(model_file)

        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name

        index_field: FormField = selected_page.findChild(FormField, "index")
        # noinspection PyTypeChecker
        index_widget: IndexWidget = index_field.widget
        assert index_field.message.text() == ""

        widget_with_table: UrlWidget | TableSelectorWidget = (
            selected_page.findChild(FormField, widget_name).widget
        )
        assert widget_with_table.table is not None

        # 1. Index values are loaded without warning messages
        def test_combo_boxes():
            index_combo_boxes: List[ComboBox] = index_field.findChildren(
                ComboBox
            )
            for ci, combo_box in enumerate(index_combo_boxes):
                # check values in ComboBox
                index_name = combo_box.objectName()
                index_values = get_index_values(
                    widget_with_table.table, index_name
                )
                index_values = list(map(str, index_values[0]))
                assert combo_box.all_items == ["None"] + index_values

                # check selection
                assert combo_box.currentText() == str(dict_values[index_name])

        test_combo_boxes()

        # 2. The internal value (in self.value) is properly stored
        for ii, index_name in enumerate(
            get_index_names(widget_with_table.table)
        ):
            assert index_widget.value.index_names[ii] == index_name
            assert (
                index_widget.value.index_values[ii] == dict_values[index_name]
            )
            # check type only with supplied values
            if dict_values[index_name] is not None:
                assert isinstance(
                    dict_values[index_name], index_widget.value.index_types[ii]
                )

        # 3. Check the return value from the widget. This returns a string or number
        # (not a list), if there is one item only
        assert index_widget.get_value_as_dict() == dict_values
        if isinstance(final_values, dict):
            assert index_widget.get_value() == final_values[widget_name]
        else:
            assert index_widget.get_value() == final_values

        # check order of index names
        index_names = list(dict_values.keys())
        if widget_name == "url":
            index_col_widget: IndexColWidget = selected_page.findChild(
                FormField, "index_col"
            ).widget
            if index_names[0] != "Anonymous index":
                assert index_col_widget.get_value() == index_names

        # 4. Test field reload - only for UrlWidget where index can be changed
        # dynamically
        if widget_name == "url":
            reload_button = widget_with_table.reload_button
            spy_index = QSignalSpy(widget_with_table.index_changed)
            spy_table = QSignalSpy(widget_with_table.updated_table)

            # field is properly reloaded. Update is triggered via index_changed
            # triggered by IndexColWidget from the updated_table Signal
            qtbot.mouseClick(reload_button, Qt.MouseButton.LeftButton)
            assert index_field.message.text() == ""
            assert spy_index.count() == 0
            assert spy_table.count() == 1
            test_combo_boxes()

        # 5. Validation
        validated = final_values is not None
        assert (
            index_widget.validate(
                "empty", "empty", index_widget.get_value()
            ).validation
            is validated
        )

        QTimer.singleShot(100, close_message_box)
        form = index_widget.form
        form_data = form.validate()

        if validated:
            assert index_field.message.text() == ""
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
            assert form_data["index"] == index_widget.get_value()

            # 6. Save form to test filter
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
                value = form.find_field_by_name(f).widget.get_value()
                if value:
                    model_param_dict[f] = value

            assert (
                model_config.parameters.get_config_from_name(param_name)
                == model_param_dict
            )
        else:
            assert form_data is False

    def test_partial_index_values(
        self, qtbot, model_file, widget_name, param_name, message
    ):
        """
        Tests that the field when the not all the index values are provided.
        In this scenario, all the values are treated as invalid.
        """
        model_config = self.get_model_config(model_file)

        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name

        index_field: FormField = selected_page.findChild(FormField, "index")
        # noinspection PyTypeChecker
        index_widget: IndexWidget = index_field.widget
        widget_with_table: UrlWidget | TableSelectorWidget = (
            selected_page.findChild(FormField, widget_name).widget
        )

        # 1. Check field
        assert message in index_field.message.text()
        for index_name in get_index_names(widget_with_table.table):
            # all indexes appear as invalid
            assert index_name in index_field.message.text()
            # the field has no selected values
            # noinspection PyTypeChecker
            combo_box: ComboBox = index_field.findChild(ComboBox, index_name)
            assert combo_box.currentText() == "None"

        # 2. returned value is an empty list
        assert index_field.value() is None

        # 3. Validation
        assert (
            index_widget.validate(
                "empty", "empty", index_widget.get_value()
            ).validation
            is False
        )

        QTimer.singleShot(100, close_message_box)
        form_data = index_widget.form.validate()
        assert form_data is False

    def test_invalid_table(
        self,
        qtbot,
        model_file,
        widget_name,
        param_name,
        dict_values,
        valid_values,
        message,
    ):
        """
        Tests the widget when the table is not valid.
        """
        model_config = self.get_model_config(model_file)

        expected_names = list(dict_values.keys())
        expected_values = list(dict_values.values())

        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name

        index_field: FormField = selected_page.findChild(FormField, "index")
        if message:
            assert message in index_field.message.text()

        # noinspection PyTypeChecker
        index_widget: IndexWidget = index_field.widget
        widget_with_table: UrlWidget | TableSelectorWidget = (
            selected_page.findChild(FormField, widget_name).widget
        )

        # 1. passed names and values are still stored
        assert index_widget.value.index_names == expected_names
        assert index_widget.value.index_values == expected_values
        # index types list is empty because table is not available
        assert index_widget.value.index_types == []
        # returned value is None
        assert index_widget.get_value() is None
        # dict value is empty dict, because table is not valid
        assert index_widget.get_value_as_dict() == {}

        # 2. Field is disabled with one ComoBox with default index name
        combo_boxes: List[ComboBox] = index_widget.findChildren(ComboBox)
        assert len(combo_boxes) == 1
        assert combo_boxes[0].isEnabled() is False
        assert combo_boxes[0].objectName() == default_index_name
        # label is set
        assert (
            index_widget.findChild(QLabel, f"{default_index_name}_label")
            is not None
        )

        # 3. Change table to one with previously stored index names and values.
        # Values are restored
        spy_updated_table = QSignalSpy(widget_with_table.updated_table)
        if widget_name == "url":
            # index_changed only applies to anonymous tables with UrlWidget
            spy_index = QSignalSpy(widget_with_table.index_changed)
            widget_with_table.line_edit.setText("files/table_mixed_types.csv")
            assert spy_index.count() == 0
        elif widget_name == "table":
            widget_with_table.combo_box.setCurrentText("csv_2_indexes_2")

        assert widget_with_table.table is not None
        assert spy_updated_table.count() == 1

        # check values - names and values sorted by DataFrame column order
        for ni, name in enumerate(index_widget.value.index_names):
            # new index was not previously set
            if name not in dict_values.keys():
                continue
            expected_value = dict_values[name]
            assert name in expected_names
            assert index_widget.value.index_values[ni] == expected_value
            assert index_widget.value.index_types[ni] == type(expected_value)

        # new CSV table has an additional index with respect to param_empty_h5_table
        # from model table with url, the index names are updated to use the only
        # index stored in the file
        if widget_name == "table" and param_name == "param_empty_h5_table":
            assert index_widget.get_value_as_dict() == {
                "Demand centre": 6,
                "Column 1": None,
            }
            assert index_widget.get_value() is None
        else:
            assert index_widget.get_value_as_dict() == dict_values
            assert index_widget.get_value() == valid_values

        # check ComboBoxes (name, values and selection)
        for name, value in dict_values.items():
            # noinspection PyTypeChecker
            combo_box: ComboBox = index_field.findChild(ComboBox, name)
            assert combo_box is not None
            assert combo_box.currentText() == str(value)
            current_values = get_index_values(widget_with_table.table, name)[0]
            assert combo_box.all_items == ["None"] + list(
                map(str, current_values)
            )

        # 4. Set now non-existing file
        if widget_name == "url":
            # Change file to non-existing one
            widget_with_table.line_edit.setText("files/table__.csv")
            # table is not available
            assert widget_with_table.table is None
            assert spy_updated_table.count() == 2

            # field is disabled and empty with one ComboBox
            assert index_field.message.text() == ""
            combo_boxes: List[ComboBox] = index_widget.findChildren(ComboBox)
            assert len(combo_boxes) == 1
            assert combo_boxes[0].isEnabled() is False
            assert combo_boxes[0].objectName() == default_index_name
            # label is set
            assert (
                index_widget.findChild(QLabel, f"{default_index_name}_label")
                is not None
            )

            # previously-set values are still stored
            for ni, name in enumerate(index_widget.value.index_names):
                expected_value = dict_values[name]
                assert name in expected_names
                assert index_widget.value.index_values[ni] == expected_value
            # types are not
            assert index_widget.value.index_types == []

            # table is not valid, field returns None
            assert index_widget.get_value() is None
            assert index_widget.get_value_as_dict() == {}

            # validation
            assert (
                index_widget.validate(
                    "empty", "empty", index_widget.get_value()
                ).validation
                is False
            )
            QTimer.singleShot(100, close_message_box)
            form_data = index_widget.form.validate()
            assert form_data is False

    def test_table_no_rows(self, qtbot):
        """
        Tests widget when the table does not contain any rows.
        """
        # test does not depend on table source widget
        model_config = self.get_model_config(self.model_files["url"])

        param_name = "param_table_no_rows"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name

        index_field: FormField = selected_page.findChild(FormField, "index")
        # noinspection PyTypeChecker
        index_widget: IndexWidget = index_field.widget
        # noinspection PyTypeChecker
        combo_box: ComboBox = index_widget.findChild(ComboBox)

        # 1. Check field value and error
        assert "does not contain any row" in index_field.message.text()
        assert combo_box.isEnabled() is False
        # although the columns are available and index names may be set, show just one
        # field with default index name
        assert combo_box.objectName() == default_index_name

        # 2. Validation
        assert (
            index_widget.validate(
                "empty", "empty", index_widget.get_value()
            ).validation
            is False
        )

        QTimer.singleShot(100, close_message_box)
        form_data = index_widget.form.validate()
        assert form_data is False

    def test_invalid_index_values(
        self,
        qtbot,
        model_file,
        widget_name,
        param_name,
        dict_values,
        expected_types,
        final_values,
        message,
    ):
        """
        Tests when the field is supplied with invalid index values.
        """
        # test does not depend on table source widget
        model_config = self.get_model_config(self.model_files["url"])

        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name

        index_field: FormField = selected_page.findChild(FormField, "index")
        # noinspection PyTypeChecker
        index_widget: IndexWidget = index_field.widget

        assert message in index_field.message.text()

        # 1. check internal values
        for ni, name in enumerate(index_widget.value.index_names):
            expected_value = dict_values[name]
            assert (
                index_widget.value.index_values[ni] is False
                if expected_value is None
                else expected_value
            )
            assert index_widget.value.index_types[ni] == expected_types[ni]

        # returned values
        assert index_widget.get_value() == final_values
        assert index_widget.get_value_as_dict() == dict_values

        # check validation method - method uses stored value. Validation is False when
        # returned value is None
        if dict_values is None:
            assert (
                index_widget.validate(
                    "empty", "empty", index_widget.get_value()
                ).validation
                is False
            )

    def test_update_values(self, qtbot):
        """
        Tests that the field values are changed the stored and returned values are
        correct.
        """
        # test does not depend on table source widget
        model_config = self.get_model_config(self.model_files["url"])

        param_name = "param_with_index_list_int"
        new_dict_values = {"Column 3": 3, "Demand centre": 2}
        new_values = [2, 3]

        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        index_widget: IndexWidget = selected_page.findChild(
            FormField, "index"
        ).widget
        combo_boxes: List[ComboBox] = index_widget.findChildren(ComboBox)

        # Change one value at the time
        for combo_box in combo_boxes:
            name = combo_box.objectName()
            new_value = str(new_dict_values[name])
            # noinspection PyUnresolvedReferences
            spy = QSignalSpy(combo_box.currentTextChanged)
            combo_box.setCurrentText(new_value)
            assert spy.count() == 1
            ii = index_widget.value.index_names.index(name)
            assert index_widget.value.index_values[ii] == new_value

        assert index_widget.get_value_as_dict() == new_dict_values
        assert index_widget.get_value() == new_values

    def test_optional_arg(self, qtbot):
        """
        Tests field validation when the field is optional.
        :param qtbot:
        :return:
        """
        model_config = self.get_model_config(self.model_files["url"])

        param_name = "param_with_index_list_int"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # noinspection PyTypeChecker
        index_field: FormField = selected_page.findChild(FormField, "index")
        # noinspection PyTypeChecker
        index_widget: IndexWidget = index_field.widget
        # mock option
        index_widget.optional = True

        index_combo_boxes: List[ComboBox] = index_field.findChildren(ComboBox)
        index_combo_boxes[0].setCurrentText("None")
        out = index_widget.validate("", "", index_widget.get_value())
        assert out.validation is True
