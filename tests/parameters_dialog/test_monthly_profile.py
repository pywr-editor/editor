import numpy as np
import pandas as pd
import pytest
import win32com.client
from functools import partial
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtWidgets import QPushButton, QLineEdit
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import (
    MonthlyValuesWidget,
    IndexWidget,
    H5KeyWidget,
    IndexColWidget,
    SheetNameWidget,
    TableSelectorWidget,
    UrlWidget,
    FormField,
)
from tests.utils import resolve_model_path, model_path, check_msg


class TestDialogParameterMonthlyValuesWidget:
    """
    Tests the ProfileWidget used to define a profile on a parameter.
    """

    model_file = resolve_model_path(
        "model_dialog_parameters_monthly_profile.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    def test_valid_parameter(self, qtbot, model_config):
        """
        Tests that the form is correctly loaded.
        """
        param_name = "valid_monthly_profile_param"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        value_field: FormField = selected_page.findChild(FormField, "values")
        # noinspection PyTypeChecker
        value_widget: MonthlyValuesWidget = value_field.widget
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )

        # 1. Test value
        assert selected_page.findChild(FormField, "name").value() == param_name
        assert value_field.message.text() == ""
        current_values = list(range(10, 130, 10))
        current_values = [c + 0.1 for c in current_values]
        assert value_field.value() == current_values
        assert save_button.isEnabled() is False

        # 2. Change value
        table = value_widget.table

        x = table.columnViewportPosition(1) + 5
        y = table.rowViewportPosition(0) + 10
        current_values[0] = 5.0
        # Double-clicking the table cell to set it into editor mode does not work.
        # Click->Double Click works, however
        qtbot.mouseClick(table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y))
        qtbot.mouseDClick(table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y))
        qtbot.keyClick(table.viewport().focusWidget(), Qt.Key_5)
        qtbot.keyClick(table.viewport().focusWidget(), Qt.Key_Enter)

        # wait to let the model update itself
        qtbot.wait(0.1)
        assert value_widget.model.values == current_values
        assert value_field.value() == current_values
        # button is enabled
        assert save_button.isEnabled() is True

        # 3. Test reset
        value_widget.reset()
        assert value_field.value() == [0] * 12

    @pytest.mark.parametrize(
        "param_name, message",
        [
            ("invalid_size_monthly_profile_param", "number of values set"),
            ("invalid_type_monthly_profile_param", "must be all numbers"),
        ],
    )
    def test_invalid_parameter(self, qtbot, model_config, param_name, message):
        """
        Tests that the form displays a warning message when the provided value is
        invalid.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        value_field: FormField = selected_page.findChild(FormField, "values")

        assert selected_page.findChild(FormField, "name").value() == param_name
        assert message in value_field.message.text()
        assert value_field.value() == [0] * 12

    def test_paste_from_excel(self, qtbot, model_config):
        """
        Tests the paste feature from Excel.
        """
        param_name = "valid_monthly_profile_param"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        value_field: FormField = selected_page.findChild(FormField, "values")
        # noinspection PyTypeChecker
        value_widget: MonthlyValuesWidget = value_field.widget
        paste_button: QPushButton = value_widget.paste_button

        # copy spreadsheet data using VBA
        excel_file = str(model_path() / "files" / "monthly_profile_vba.xlsm")
        vba_module = "monthly_profile_vba.xlsm!MainModule"
        xl = win32com.client.Dispatch("Excel.Application")
        xl.Workbooks.Open(
            excel_file,
            ReadOnly=1,
        )

        # valid clipboard data
        xl.Application.Run(f"{vba_module}.CopyToClipboardAll")
        table = pd.read_excel(excel_file, sheet_name="Valid")
        qtbot.mouseClick(paste_button, Qt.MouseButton.LeftButton)
        assert all(np.equal(value_widget.get_value(), table["Value"].values))

        # invalid data
        routines = [
            "CopyToClipboardPartial",
            "CopyToClipboardInvalid",
            "CopyToClipboardTable",
        ]
        messages = [
            "must contain 12 values,",
            "must contain 12 numbers",
            "must contain 12 numbers",
        ]
        for routine, message in zip(routines, messages):
            xl.Application.Run(f"{vba_module}.{routine}")

            QTimer.singleShot(100, partial(check_msg, message))
            qtbot.mouseClick(paste_button, Qt.MouseButton.LeftButton)
            assert all(
                np.equal(value_widget.get_value(), table["Value"].values)
            )

        xl.Quit()

    # noinspection PyTypeChecker
    def test_profile_with_url(self, qtbot, model_config):
        """
        Tests that the widgets load properly and the form is correctly saved when the
        profile is provided via an external file. This does not test individual
        widgets, but the general form behaviour. Widget-specific tests are performed
        separately.
        """
        param_name = "monthly_profile_param_url"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        fields: dict[str, FormField] = {}
        widgets = {}
        for name in ["url", "index_col", "sheet_name", "index"]:
            fields[name] = selected_page.findChild(FormField, name)
            widgets[name] = fields[name].widget

        # 1. UrlWidget - table is loaded (parse_dates is N/A - not supported by
        # parameter)
        url_widget: UrlWidget = fields["url"].widget
        assert url_widget.full_file is not None
        table = pd.read_excel(
            url_widget.full_file, sheet_name="Horizontal_table"
        )
        assert table.equals(url_widget.table)
        assert url_widget.table.attrs["index"] == ["Index 1", "Index 2"]

        # 2. IndexColWidget - multi-index
        index_col_widget: IndexColWidget = fields["index_col"].widget
        assert index_col_widget.get_value() == ["Index 1", "Index 2"]

        # 3. IndexWidget
        index_widget: IndexWidget = fields["index"].widget
        assert index_widget.get_value() == ["A", "C"]

        # 5. SheetNameWidget
        sheet_name_widget: SheetNameWidget = fields["sheet_name"].widget
        assert sheet_name_widget.get_value() == "Horizontal_table"

        # 6. Save form
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        # button is disabled
        assert save_button.isEnabled() is False
        comment_widget: QLineEdit = selected_page.findChild(
            FormField, "comment"
        ).widget
        comment_widget.setText("Updated by me")
        assert save_button.isEnabled() is True

        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        for field in fields.values():
            assert field.message.text() == ""

        assert model_config.has_changes is True
        assert model_config.parameters.get_config_from_name(param_name) == {
            "type": "monthlyprofile",
            "url": url_widget.get_value(),
            "sheet_name": "Horizontal_table",
            "index_col": ["Index 1", "Index 2"],
            "index": ["A", "C"],
            "comment": "Updated by me",
        }

    def test_profile_with_url_h5(self, qtbot, model_config):
        """
        Tests that the widgets load properly and the form is correctly saved when the
        profile is provided using an external H5 file. This does not test individual
        widgets, but the general form behaviour. Widget-specific tests are performed
         separately.
        """
        param_name = "monthly_profile_param_url_h5"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        fields: dict[str, FormField] = {}
        widgets = {}
        for name in ["url", "index_col", "key", "index"]:
            # noinspection PyTypeChecker
            fields[name] = selected_page.findChild(FormField, name)
            widgets[name] = fields[name].widget

        # 1. UrlWidget - table is loaded (parse_dates is N/A - not supported by
        # parameter)
        url_widget: UrlWidget = fields["url"].widget
        assert url_widget.full_file is not None
        # noinspection PyTypeChecker
        table: pd.DataFrame = pd.read_hdf(
            url_widget.full_file, key="monthly_profile"
        )
        table.reset_index(inplace=True)
        assert table.equals(url_widget.table)
        assert url_widget.table.attrs["index"] == ["Index 1"]

        # 2. IndexColWidget - this is hidden
        index_col_widget: IndexColWidget = fields["index_col"].widget
        assert index_col_widget.isVisible() is False
        assert index_col_widget.get_value() == ["Index 1"]

        # 3. IndexWidget
        index_widget: IndexWidget = fields["index"].widget
        assert index_widget.get_value() == "A"

        # 5. H5KeyWidget
        key_widget: H5KeyWidget = fields["key"].widget
        assert key_widget.get_value() == "/monthly_profile"

        # 6. Save form
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        # button is disabled
        assert save_button.isEnabled() is False
        comment_widget: QLineEdit = selected_page.findChild(
            FormField, "comment"
        ).widget
        comment_widget.setText("Updated by me")
        assert save_button.isEnabled() is True

        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        for field in fields.values():
            assert field.message.text() == ""

        assert model_config.has_changes is True
        assert model_config.parameters.get_config_from_name(param_name) == {
            "type": "monthlyprofile",
            "url": url_widget.get_value(),
            "key": "/monthly_profile",
            "index": "A",
            "comment": "Updated by me",
        }

    def test_profile_with_table(self, qtbot, model_config):
        """
        Tests that the widgets load properly and the form is correctly saved when the
        profile is provided using a table. This does not test individual widgets, but
        the general form behaviour. Widget-specific tests are performed separately.
        """
        param_name = "monthly_profile_param_table"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        fields: dict[str, FormField] = {}
        widgets = {}
        for name in ["table", "index"]:
            fields[name] = selected_page.findChild(FormField, name)
            widgets[name] = fields[name].widget

        # 1. TableSelectorWidget - table is loaded
        table_widget: TableSelectorWidget = fields["table"].widget
        assert table_widget.file is not None
        table = pd.read_excel(table_widget.file, sheet_name="Horizontal_table")
        assert table.equals(table_widget.table)
        assert table_widget.table.attrs["index"] == ["Index 1", "Index 2"]

        # 2. IndexWidget
        index_widget: IndexWidget = fields["index"].widget
        assert index_widget.get_value() == ["A", "C"]

        # 3. Save form
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        # button is disabled
        assert save_button.isEnabled() is False
        comment_widget: QLineEdit = selected_page.findChild(
            FormField, "comment"
        ).widget
        comment_widget.setText("Updated by me")
        assert save_button.isEnabled() is True

        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        for field in fields.values():
            assert field.message.text() == ""

        assert model_config.has_changes is True
        assert model_config.parameters.get_config_from_name(param_name) == {
            "type": "monthlyprofile",
            "table": "profile_table",
            "index": ["A", "C"],
            "comment": "Updated by me",
        }
