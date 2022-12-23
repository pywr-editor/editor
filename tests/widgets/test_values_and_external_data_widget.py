from functools import partial
from pathlib import Path

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.form import (
    ColumnWidget,
    ExternalDataPickerDialogWidget,
    FormCustomWidget,
    FormField,
    IndexColWidget,
    IndexWidget,
    ParameterForm,
    SourceSelectorWidget,
    TableSelectorWidget,
    UrlWidget,
    ValuesAndExternalDataWidget,
)
from pywr_editor.model import ModelConfig, ParameterConfig
from pywr_editor.widgets import ComboBox, PushButton
from tests.DummyMainWindow import MainWindow
from tests.utils import check_msg, resolve_model_path


class TestDialogParameterValuesAndExternalDataWidget:
    """
    Tests the ValuesAndExternalDataWidget.
    """

    @staticmethod
    def widget(
        value: list[int | float] | dict | None,
        field_args: dict | None = None,
    ) -> ValuesAndExternalDataWidget:
        """
        Initialises the form and returns the widget.
        :param value: A list of numbers or dictionary to fetch external data.
        :param field_args: Additional field arguments to pass to the widget.
        :return: An instance of ValuesAndExternalDataWidget.
        """
        # mock widgets
        form = ParameterForm(
            model_config=ModelConfig(resolve_model_path("model_tables.json")),
            parameter_obj=ParameterConfig({}),
            available_fields={
                "Section": [
                    {
                        "name": "value",
                        "field_type": ValuesAndExternalDataWidget,
                        "field_args": field_args,
                        "value": value,
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        form.enable_optimisation_section = False
        form.load_fields()

        form_field = form.find_field_by_name("value")
        # noinspection PyTypeChecker
        return form_field.widget

    @pytest.mark.parametrize(
        "value, field_args, combo_box_key, expected_value",
        [
            # values provided
            (
                [1.02, 234, 12.56, 99, -12],
                None,
                "values",
                [1.02, 234, 12.56, 99, -12],
            ),
            # dictionary configuration
            ({"url": "file.csv"}, None, "external", {"url": "file.csv"}),
            ({"table": "Table 1"}, None, "external", {"table": "Table 1"}),
            # default to "values" (None)
            (None, None, "values", []),
            # empty dictionary w/o minimum requirement
            ({}, None, "external", {}),
            # multiple variables
            [
                [[1.02, 234], [12.56, 99]],
                {"multiple_variables": True, "variable_names": ["x", "y"]},
                "values",
                [[1.02, 234], [12.56, 99]],
            ],
            # multiple variables but with external data
            [
                {"url": "file.csv"},
                {"multiple_variables": True, "variable_names": ["x", "y"]},
                "external",
                {"url": "file.csv"},
            ],
        ],
    )
    def test_valid(
        self, qtbot, value, field_args, combo_box_key, expected_value
    ):
        """
        Tests that the field is loaded correctly.
        """
        widget = self.widget(value=value, field_args=field_args)
        form_field: FormField = widget.form_field

        # register app to test field visibility
        app = MainWindow("")
        app.setCentralWidget(widget)
        qtbot.addWidget(app)
        app.show()
        qtbot.waitForWindowShown(app)

        # 1. Check field
        assert form_field.message.text() == ""
        assert (
            widget.combo_box.currentText() == widget.labels_map[combo_box_key]
        )
        assert widget.get_value() == expected_value

        # 2. Check visibility of the table, buttons and line edit field
        if combo_box_key == "values":
            # table
            assert widget.table.isVisible() is True
            for button in widget.table_buttons:
                assert button.isVisible() is True

            # QLineEdit
            assert widget.line_edit_widget_container.isVisible() is False
            assert widget.line_edit.text() == "None"
            assert widget.external_data_dict is None
        elif combo_box_key == "external":
            # table
            assert widget.table.isVisible() is False
            for button in widget.table_buttons:
                assert button.isVisible() is False

            # QLineEdit
            assert widget.line_edit_widget_container.isVisible() is True
            assert isinstance(widget.external_data_dict, dict) is True
            if "url" in widget.external_data_dict:
                assert (
                    widget.external_data_dict["url"] in widget.line_edit.text()
                )
            if "table" in widget.external_data_dict:
                assert (
                    widget.external_data_dict["table"]
                    in widget.line_edit.text()
                )

        # 3. Validation
        out = widget.validate("", "", widget.get_value())
        assert out.validation is True

        # 4. Test reset
        widget.reset()
        assert widget.line_edit.text() == "None"
        assert widget.external_data_dict is None
        if field_args and "multiple_variables" in field_args:
            assert widget.model.values == [[] for _ in range(0, len(value))]
        else:
            assert widget.model.values == [[]]
        # default choice
        assert widget.combo_box.currentText() == widget.labels_map["values"]

        # 5. Change value and test field visibility
        if combo_box_key == "values":
            widget.combo_box.setCurrentText(widget.labels_map["external"])
            assert widget.table.isVisible() is False
            for button in widget.table_buttons:
                assert button.isVisible() is False
            assert widget.line_edit_widget_container.isVisible() is True
        else:
            widget.combo_box.setCurrentText(widget.labels_map["values"])
            assert widget.table.isVisible() is True
            for button in widget.table_buttons:
                assert button.isVisible() is True
            assert widget.line_edit_widget_container.isVisible() is False

    @pytest.mark.parametrize(
        "value, field_args, combo_box_key, init_message, validation_message",
        [
            # wrong keys in dictionary, validation passes
            (
                {"a": 1},
                None,
                "external",
                None,
                None,
            ),
            # wrong keys in dictionary, validation fails (values > 0, parameter
            # required)
            (
                {"a": 1},
                {"min_total_values": 15},
                "external",
                "external data is not valid",
                "You must configure the field",
            ),
            # wrong parameter type in dictionary, validation fails (values > 0,
            # parameter required)
            (
                {"a": 1},
                {"min_total_values": 5},
                "external",
                "external data is not valid",
                "You must configure the field",
            ),
            (
                {},
                {"min_total_values": 5},
                "external",
                "external data is not valid",
                "You must configure the field",
            ),
            # default to "values" when type is wrong. Handled by TableValuesWidget
            (
                False,
                None,
                "values",
                "must be all valid lists",
                None,
            ),
            # default to "values" when type is wrong. Handled by TableValuesWidget
            (
                False,
                {"min_total_values": 5},
                "values",
                "must be all valid lists",
                "at least 5 values",
            ),
            # value is a list of nested list instead of numbers - handled by
            # parent widget
            (
                [[1.02, 234, 12.56], [99, -12, 176]],
                {"min_total_values": 5},
                "values",
                "can only contain numbers",
                "at least 5 values",
            ),
            # multiple variables - nested list size does not match variable number
            [
                [[1.02, 234], [12.56, 99]],
                {"multiple_variables": True, "variable_names": ["x", "y", "z"]},
                "values",
                "number of values must be the same",
                None,
            ],
            # multiple variables - nested list size less than min_total_values
            [
                [[1.02, 234], [12.56, 99]],
                {
                    "multiple_variables": True,
                    "min_total_values": 5,
                    "variable_names": ["x", "y"],
                },
                "values",
                "points must be at least 5",
                "provide at least 5 values",
            ],
        ],
    )
    def test_invalid(
        self,
        qtbot,
        value,
        field_args,
        combo_box_key,
        init_message,
        validation_message,
    ):
        """
        Tests that the form displays a warning message when the provided value is
        invalid.
        """
        widget = self.widget(value=value, field_args=field_args)
        form_field: FormField = widget.form_field

        # register app to test field visibility
        app = MainWindow("")
        app.setCentralWidget(widget)
        qtbot.addWidget(app)
        app.show()
        qtbot.waitForWindowShown(app)

        # 1. Check field
        if init_message is None:
            assert form_field.message.text() == ""
        else:
            assert init_message in form_field.message.text()
        assert (
            widget.combo_box.currentText() == widget.labels_map[combo_box_key]
        )

        # 2. Check QLineEdit
        line_edit = widget.line_edit
        if combo_box_key == "values":
            assert line_edit.isVisible() is False
        else:
            assert line_edit.isVisible() is True
            # dictionary stored internally, but QLineEdit is empty
            assert widget.external_data_dict == value
            assert widget.line_edit.text() == "None"

        # 3. Validation
        out = widget.validate("", "", widget.get_value())
        if validation_message is None:
            assert out.validation is True
        else:
            assert out.validation is False
            assert validation_message in out.error_message

    # noinspection PyTypeChecker
    @pytest.mark.parametrize(
        "value",
        [
            {
                "url": "files\\table.csv",
                "index_col": ["Column 1"],
                "column": "Column 3",
            },
            {"table": "Table 7", "index": 8},
        ],
    )
    def test_picker_dialog(self, qtbot, value):
        """
        Tests the ExternalDataPickerDialogWidget.
        """
        widget = self.widget(
            value=value,
        )

        # 1. Open the dialog
        select_button: PushButton = (
            widget.line_edit_widget_container.findChildren(PushButton)[0]
        )
        qtbot.mouseClick(select_button, Qt.MouseButton.LeftButton)
        child_dialog: ExternalDataPickerDialogWidget = (
            widget.form.parent.findChild(ExternalDataPickerDialogWidget)
        )

        # 2. Check the values in the child form
        values_dict = None
        if "url" in value:
            values_dict = {
                SourceSelectorWidget: "anonymous_table",
                UrlWidget: str(Path(value["url"])),
                IndexColWidget: value["index_col"],
                IndexWidget: None,
                ColumnWidget: value["column"],
            }
        elif "table" in value:
            values_dict = {
                SourceSelectorWidget: "table",
                TableSelectorWidget: value["table"],
                IndexWidget: value["index"],
                ColumnWidget: None,
            }

        for widget_class, value_to_check in values_dict.items():
            child_widget: FormCustomWidget = child_dialog.findChild(
                widget_class
            )
            assert child_widget.form_field.message.text() == ""
            if widget_class == SourceSelectorWidget:
                child_widget: SourceSelectorWidget
                assert (
                    child_widget.get_value()
                    == child_widget.labels[value_to_check]
                )
                continue

            if value_to_check is None:
                assert child_widget.get_value() is None
            else:
                assert child_widget.get_value() == value_to_check

        # 3. Change a form value, submit the form and check the parent widget value
        child_form = None
        if "url" in value:
            column_widget: ColumnWidget = child_dialog.findChild(ColumnWidget)
            child_form = column_widget.form

            new_column = "Demand centre"
            column_widget.combo_box.setCurrentText(new_column)
            value["column"] = new_column
        elif "table" in value:
            index_widget: IndexWidget = child_dialog.findChild(IndexWidget)
            child_form = index_widget.form

            new_index = 4
            combo_box: ComboBox = index_widget.findChild(ComboBox)
            combo_box.setCurrentText(str(new_index))
            value["index"] = new_index

        # submit the form
        # manually enable the button
        child_save_button = child_form.save_button
        child_save_button.setEnabled(True)
        qtbot.mouseClick(child_save_button, Qt.MouseButton.LeftButton)
        child_dialog.close()

        # check dictionary in main widget
        assert widget.external_data_dict == value
        assert widget.get_value() == value

        # 4. Open the dialog again and
        #  - for URL, set both index and column to raise an error
        #  - for table, remove index and column to raise an error
        qtbot.mouseClick(select_button, Qt.MouseButton.LeftButton)
        column_widget: ColumnWidget = child_dialog.findChild(ColumnWidget)
        message = None
        if "url" in value:
            column_widget.combo_box.setCurrentText("None")
            assert column_widget.get_value() is None

            message = "must select an index or column name"
        elif "table" in value:
            new_column = "Column 1"
            column_widget.combo_box.setCurrentText(new_column)
            assert column_widget.get_value() == new_column
            message = "You cannot select both"

        # send form and verify message
        QTimer.singleShot(100, partial(check_msg, message))
        child_save_button.setEnabled(True)
        qtbot.mouseClick(child_save_button, Qt.MouseButton.LeftButton)
