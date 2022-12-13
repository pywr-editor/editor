import pandas as pd
import pytest
from PySide6.QtCore import QTimer
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import SheetNameWidget, UrlWidget, FormField
from pywr_editor.utils import get_index_names
from tests.utils import resolve_model_path, close_message_box


class TestDialogParameterSheetNameWidget:
    """
    Tests the SheetName widget in the parameter dialog. This applies to anonymous
    tables of Excel type only.
    """

    model_file = resolve_model_path("model_dialog_parameters_sheet_h5key.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """

        return ModelConfig(self.model_file)

    def test_excel_sheet(self, qtbot, model_config):
        """
        Tests that the url and excel_sheet widgets behave correctly when an Excel file
        is set using an anonymous table.
        """
        # load a valid table
        selected_parameter = "param_with_valid_excel_table"
        dialog = ParametersDialog(model_config, selected_parameter)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        excel_sheet_field: FormField = selected_page.findChild(
            FormField, "sheet_name"
        )
        excel_sheet_widget: SheetNameWidget = excel_sheet_field.widget
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget

        # 1. the table is properly loaded
        assert url_widget.table.equals(
            pd.read_excel(
                url_widget.full_file, sheet_name=excel_sheet_widget.value
            )
        )
        assert url_widget.file_ext == ".xlsx"

        # 2. available sheets and selected sheet are correctly set
        assert (
            selected_page.findChild(FormField, "name").value()
            == selected_parameter
        )
        assert excel_sheet_field.value() == "Sheet 3"
        assert excel_sheet_field.message.text() == ""
        assert excel_sheet_widget.combo_box.all_items == [
            "Sheet 1",
            "Sheet 2",
            "Sheet 3",
        ]

        # 2a. test validate method
        output = excel_sheet_widget.validate(
            "sheet", "Sheet", excel_sheet_widget.get_value()
        )
        assert output.validation is True

        # 2b. test form validation - a valid dictionary is returned without error
        # message on the field skip other invalid fields
        QTimer.singleShot(100, close_message_box)
        form_data = url_widget.form.validate()
        assert excel_sheet_field.message.text() == ""
        assert isinstance(form_data, dict)
        assert form_data["name"] == selected_parameter
        assert form_data["type"] == "constant"
        assert form_data["url"] == url_widget.get_value()
        assert form_data["sheet_name"] == excel_sheet_widget.get_value()

        # 3. changing the active sheet, reloads the table (Signal acts on text changes)
        new_sheet = "Sheet 2"
        excel_sheet_widget.combo_box.setCurrentText(new_sheet)
        assert excel_sheet_field.value() == new_sheet
        assert excel_sheet_field.message.text() == ""
        assert url_widget.table.equals(
            pd.read_excel(url_widget.full_file, sheet_name=new_sheet)
        )

        # 4. set non-existing file, then set same XLSX file. Table must be reloaded
        # and same sheet selected validation check not necessary because field is
        # hidden and disabled when file does not exist
        original_file = url_widget.full_file
        url_widget.line_edit.setText(original_file[0:-1])
        assert "not exist" in url_widget.form_field.message.text()
        # File does not exist and table is invalid
        assert url_widget.full_file is None
        assert url_widget.file_ext == ".xls"
        assert url_widget.table is None

        # The sheet widget is disabled, empty and still visible (XLS file)
        assert excel_sheet_widget.isEnabled() is False
        assert excel_sheet_widget.combo_box.all_items == []
        assert excel_sheet_widget.combo_box.currentText() == ""

        # Set original value
        url_widget.line_edit.setText(original_file)
        assert url_widget.form_field.message.text() == ""
        assert url_widget.full_file == original_file
        assert url_widget.file_ext == ".xlsx"
        assert url_widget.table.equals(
            pd.read_excel(url_widget.full_file, sheet_name=new_sheet)
        )

        # 5. Load a new Excel file. Table must be reloaded and first sheet selected
        url_widget.line_edit.setText(r"files/table2.xlsx")
        assert url_widget.form_field.message.text() == ""
        assert url_widget.file_ext == ".xlsx"
        first_sheet = "Demand centres"
        assert url_widget.table.equals(
            pd.read_excel(url_widget.full_file, sheet_name=first_sheet)
        )
        assert excel_sheet_widget.isEnabled() is True
        assert excel_sheet_widget.combo_box.all_items == [
            first_sheet,
            "Inflows",
            "OWE",
        ]
        assert excel_sheet_widget.combo_box.currentText() == first_sheet
        assert excel_sheet_widget.value == first_sheet

    def test_excel_non_existing_sheet(self, qtbot, model_config):
        """
        Tests that, when a non-existing sheet is provided, the first sheet is selected
        and a warning message is shown.
        """
        selected_parameter = "param_with_excel_table_wrong_sheet"
        dialog = ParametersDialog(model_config, selected_parameter)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        excel_sheet_field: FormField = selected_page.findChild(
            FormField, "sheet_name"
        )
        excel_sheet_widget: SheetNameWidget = excel_sheet_field.widget
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget
        form = url_widget.form
        first_sheet = "Sheet 1"

        assert (
            selected_page.findChild(FormField, "name").value()
            == selected_parameter
        )
        assert (
            "does not exist in the Excel file"
            in excel_sheet_field.message.text()
        )
        # 1. the first sheet is selected
        assert excel_sheet_field.value() == first_sheet
        # 2. check table in first sheet
        df = pd.read_excel(url_widget.full_file, sheet_name=first_sheet)
        assert url_widget.table.equals(df)
        # check its index
        assert get_index_names(url_widget.table) == [df.columns.values[2]]

        # 3. test validate method
        output = excel_sheet_widget.validate(
            "sheet", "Sheet", excel_sheet_widget.get_value()
        )
        assert output.validation is True

        # 4. test form validation - validation passes because first sheet is selected
        QTimer.singleShot(100, close_message_box)
        form_data = form.validate()
        assert excel_sheet_field.message.text() == ""
        assert isinstance(form_data, dict)
        assert form_data["name"] == selected_parameter
        assert form_data["type"] == "constant"
        assert form_data["url"] == url_widget.get_value()
        assert form_data["sheet_name"] == first_sheet
