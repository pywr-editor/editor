import pandas as pd
import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import FormField, ParameterForm, TableSelectorWidget
from pywr_editor.model import ModelConfig, ParameterConfig
from pywr_editor.utils import default_index_name, get_index_names
from pywr_editor.widgets import ComboBox
from tests.utils import close_message_box, model_path, resolve_model_path
from tests.widgets.test_url_widget import df_from_h5


class TestDialogParameterTableSelectorWidget:
    """
    Tests the TableSelectorWidget in the parameter dialog. This is used for
    non-anonymous tables only.
    """

    model_file = resolve_model_path(
        "model_dialog_parameters_table_selector_widget.json"
    )
    model_file_empty = resolve_model_path("model_4.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.fixture()
    def model_config_empty_table(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file_empty)

    @pytest.mark.parametrize(
        "param_name, selected_table, table_file, expected_indexes",
        [
            (
                "param_csv_file",
                "csv_table",
                "files/table.csv",
                ["Column 1", "Demand centre"],
            ),
            (
                "param_csv_table_no_index_col",
                "csv_table_no_index_col",
                "files/table.csv",
                [default_index_name],
            ),
            ("param_excel_file", "excel_file", "files/table2.xlsx", ["Centre"]),
            # indexes are built-in (Anonymous)
            ("param_h5_file", "h5_table", "files/table.h5", []),
        ],
    )
    def test_valid_table_file(
        self,
        qtbot,
        model_config,
        param_name,
        selected_table,
        table_file,
        expected_indexes,
    ):
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        table_field: FormField = selected_page.findChild(FormField, "table")
        # noinspection PyTypeChecker
        table_widget: TableSelectorWidget = table_field.widget
        dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name
        table_names = list(model_config.tables.get_all().keys())

        # 1. The table selector field is enabled without errors or warnings
        assert table_widget.isEnabled() is True
        assert table_widget.get_value() == selected_table
        assert table_widget.combo_box.all_items == ["None"] + table_names
        assert table_field.message.text() == ""
        table_file = str(model_path() / table_file)
        assert table_widget.file == table_file

        if "csv" in table_file:
            comp_table = pd.read_csv(table_file)
            assert table_widget.file_ext == ".csv"
            index_names = expected_indexes
        elif "h5" in table_file:
            comp_table, index_names = df_from_h5(table_file, key="/flow")
            assert table_widget.file_ext == ".h5"
        else:
            comp_table = pd.read_excel(table_file)
            assert table_widget.file_ext == ".xlsx"
            index_names = expected_indexes

        assert table_widget.table.equals(comp_table)
        assert get_index_names(table_widget.table) == index_names

        # 2. Buttons are enabled
        assert table_widget.open_button.isEnabled() is True
        assert table_widget.reload_button.isEnabled() is True

        # 3. Try reloading the table
        spy = QSignalSpy(table_widget.updated_table)
        assert spy.count() == 0
        qtbot.mouseClick(table_widget.reload_button, Qt.MouseButton.LeftButton)
        assert table_widget.table.equals(comp_table)
        assert spy.count() == 1

        # 3. test validate method
        output = table_widget.validate(
            "table", "Table", table_widget.get_value()
        )
        assert output.validation is True

        # 4. test form validation - a valid dictionary is returned without error
        # message on the field
        form = table_widget.form
        form_data = form.validate()
        assert table_field.message.text() == ""
        assert isinstance(form_data, dict)
        assert form_data["name"] == param_name
        assert form_data["type"] == "constant"
        assert "url" not in form_data
        assert form_data["table"] == table_widget.get_value()

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

        fields = ["table", "index", "column"]
        model_param_dict = {"type": "constant"}
        for f in fields:
            model_param_dict[f] = form.find_field_by_name(f).widget.get_value()

        assert (
            model_config.parameters.get_config_from_name(param_name)
            == model_param_dict
        )

        # 6. Change the value
        combo_box = table_widget.combo_box
        new_table = "another_csv_table"
        spy = QSignalSpy(combo_box.currentTextChanged)
        assert spy.count() == 0
        combo_box.setCurrentText(new_table)

        # Signal is emitted
        assert spy.count() == 1
        # check value
        assert table_widget.value == new_table
        # check file and content
        table_file = str(model_path() / "files" / "table_mixed_types.csv")
        assert table_widget.file == table_file
        assert table_widget.file_ext == ".csv"
        assert table_widget.table.equals(pd.read_csv(table_file))

    @pytest.mark.parametrize(
        "param_name, selected_table, init_message, validation_message",
        [
            (
                "param_non_existing_file",
                "non_existing_file",
                "The table file does not exist",
                "The table file is not valid",
            ),
            (
                "param_file_ext_not_supported",
                "file_ext_not_supported",
                "is not supported",
                "The table file is not valid",
            ),
            (
                "param_file_non_parsable",
                "non_parsable_table",
                "",
                "The table file is not valid",
            ),
            (
                "param_wrong_table_type",
                None,
                "must be a string",
                "must select a valid table",
            ),
        ],
    )
    def test_invalid_table_file(
        self,
        qtbot,
        model_config,
        param_name,
        selected_table,
        init_message,
        validation_message,
    ):
        """
        Test the widget when the table file does not exist or is not supported.
        """
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        table_field: FormField = selected_page.findChild(FormField, "table")
        # noinspection PyTypeChecker
        table_widget: TableSelectorWidget = table_field.widget
        dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. the table selector field is enabled but with errors or warnings
        assert table_widget.isEnabled() is True
        assert table_widget.get_value() == selected_table
        assert init_message in table_field.message.text()
        assert table_widget.table is None

        # 2. check buttons status
        assert table_widget.open_button.isEnabled() is False
        # if file is not available, user can reload if it is later created
        if param_name == "param_non_existing_file":
            assert table_widget.reload_button.isEnabled() is True
        # if extension is wrong or file is not parsable, refresh is disabled
        else:
            assert table_widget.reload_button.isEnabled() is False

        # 3. test validate method
        output = table_widget.validate(
            "table", "Table", table_widget.get_value()
        )
        assert output.validation is False
        assert validation_message in output.error_message

        # 4. test form validation - False is returned with an error message set on
        # the field
        QTimer.singleShot(100, close_message_box)
        form_data = table_widget.form.validate()
        assert form_data is False
        assert validation_message in table_field.message.text()

    def test_invalid_table_name(self, qtbot, model_config):
        """
        Test the widget when the provided table name does not exist in the model
        tables.
        """
        param_name = "param_file_invalid_table_name"
        selected_table = "non_existing_table"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        table_field: FormField = selected_page.findChild(FormField, "table")
        # noinspection PyTypeChecker
        table_widget: TableSelectorWidget = table_field.widget
        dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name

        # the ComboBox is enabled but with a warning message
        assert table_widget.combo_box.isEnabled() is True
        assert table_widget.combo_box.currentText() == "None"
        # value is still stored
        assert table_widget.value == selected_table
        assert table_widget.get_value() is None
        assert "does not exist" in table_field.message.text()

        # 2. buttons are disabled
        assert table_widget.open_button.isEnabled() is False
        assert table_widget.reload_button.isEnabled() is False

        # 3. test validate method
        message = "You must select a valid table from the list"
        output = table_widget.validate(
            "table", "Table", table_widget.get_value()
        )
        assert output.validation is False
        assert message in output.error_message

        # 4. test form validation - False is returned with an error message set on
        # the field
        QTimer.singleShot(100, close_message_box)
        form_data = table_widget.form.validate()
        assert form_data is False
        assert message in table_field.message.text()

    def test_tables_not_available(self, qtbot, model_config_empty_table):
        """
        Test the widget when the no tables are provided in the model configuration.
        """
        param_name = "param4"
        dialog = ParametersDialog(model_config_empty_table, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        table_field: FormField = selected_page.findChild(FormField, "table")
        # noinspection PyTypeChecker
        table_widget: TableSelectorWidget = table_field.widget
        dialog.hide()

        assert selected_page.findChild(FormField, "name").value() == param_name

        assert table_widget.combo_box.isEnabled() is False
        assert table_widget.combo_box.currentText() == "None"
        assert "no tables defined" in table_field.message.text()

        # 2. buttons are disabled
        assert table_widget.open_button.isEnabled() is False
        assert table_widget.reload_button.isEnabled() is False

        # 3. test validate method
        message = "You must select a valid table from the list"
        output = table_widget.validate(
            "table", "Table", table_widget.get_value()
        )
        assert output.validation is False
        assert output.error_message == message

        # 4. test form validation - False is returned with an error message set on
        # the field
        QTimer.singleShot(100, close_message_box)
        form_data = table_widget.form.validate()
        assert form_data is False
        assert table_field.message.text() == message

    def test_reset(self, qtbot, model_config):
        """
        Tests the reset method
        """
        param_name = "param_csv_file"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        table_field: FormField = selected_page.findChild(FormField, "table")
        # noinspection PyTypeChecker
        table_widget: TableSelectorWidget = table_field.widget

        dialog.hide()
        spy = QSignalSpy(table_widget.updated_table)
        table_widget.reset()

        assert spy.count() == 1
        # field is reset/empty
        assert table_widget.isEnabled() is True
        assert table_widget.table is None
        assert table_widget.combo_box.currentText() == "None"

    def test_parse_error_h5(self, qtbot, model_config):
        """
        Tests that, when the file cannot be parsed (for example when a data store does
        not have any key), the field is disabled with a warning message and the other
        fields are shown to let user change the parser options.
        """
        selected_parameter = "param_with_h5_no_keys"
        dialog = ParametersDialog(model_config, selected_parameter)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()
        table_field: FormField = selected_page.findChild(FormField, "table")
        # noinspection PyTypeChecker
        table_widget: TableSelectorWidget = table_field.widget

        assert (
            selected_page.findChild(FormField, "name").value()
            == selected_parameter
        )
        assert "Cannot parse the file" in table_field.message.text()

        # common fields are visible but disabled
        for field_name in ["index", "column"]:
            shown_field: FormField = selected_page.findChild(
                FormField, field_name
            )
            assert shown_field.isVisible() is True

            if field_name != "index":
                assert shown_field.widget.combo_box.isEnabled() is False
            else:
                assert all(
                    [
                        f.isEnabled() is False
                        for f in shown_field.findChildren(ComboBox)
                    ]
                )

        # 3. test validate method
        message = "The table file is not valid"
        output = table_widget.validate(
            "table", "Table", table_widget.get_value()
        )
        assert output.validation is False
        assert message in output.error_message

        # 4. test form validation - False is returned with an error message set on the
        # field
        QTimer.singleShot(100, close_message_box)
        form_data = table_widget.form.validate()
        assert form_data is False
        assert message in table_field.message.text()

    @pytest.mark.parametrize(
        "selected_table, empty_model, init_message, value",
        [
            # parsing/file errors are suppressed
            ("non_existing_table", False, None, None),
            ("param_file_ext_not_supported", False, None, None),
            ("param_file_non_parsable", False, None, None),
            # no model tables
            (None, True, "no tables defined", None),
            # valid table
            (
                "csv_table",
                False,
                None,
                "csv_table",
            ),
        ],
    )
    def test_is_static(
        self, qtbot, selected_table, empty_model, init_message, value
    ):
        """
        Checks when the static argument is set to True.
        """
        if empty_model:
            model_file = self.model_file_empty
        else:
            model_file = self.model_file

        # mock widgets
        form = ParameterForm(
            model_config=ModelConfig(model_file),
            parameter_obj=ParameterConfig({}),
            available_fields={
                "Section": [
                    {
                        "name": "value",
                        "field_type": TableSelectorWidget,
                        "field_args": {"static": True},
                        "value": selected_table,
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        form.enable_optimisation_section = False
        form.load_fields()

        form_field = form.find_field_by_name("value")

        # buttons are hidden
        assert not form_field.findChild(QPushButton) is True

        # check init message
        if init_message:
            assert init_message in form_field.message.text()
        else:
            assert form_field.message.text() == ""

        # check values
        assert form_field.value() == value
        assert form_field.widget.file is None
