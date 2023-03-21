from functools import partial
from typing import List

import pandas as pd
import pytest
from PySide6.QtCore import QItemSelectionModel, QTimer
from PySide6.QtGui import Qt
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication, QGroupBox, QLabel, QPushButton

from pywr_editor.dialogs import TablesDialog
from pywr_editor.dialogs.tables.table_empty_page_widget import (
    TableEmptyPageWidget,
)
from pywr_editor.dialogs.tables.table_url_widget import TableUrlWidget
from pywr_editor.form import FormField, IndexColWidget
from pywr_editor.model import ModelConfig
from pywr_editor.utils import get_index_names
from tests.utils import check_msg, close_message_box, resolve_model_path
from tests.widgets.test_url_widget import df_from_h5


# noinspection PyTypeChecker
class TestTablesDialog:
    model_file = resolve_model_path("model_tables.json")
    model_file_table_selector = resolve_model_path(
        "model_dialog_parameters_table_selector_widget.json"
    )

    csv_fields = [
        "sep",
        "dayfirst",
        "skipinitialspace",
        "skipfooter",
        "skip_blank_lines",
    ]
    excel_fields = ["sheet_name"]
    h5_fields = ["key", "start"]
    hidden_h5_fields = [
        "index_col",
        "parse_dates",
    ]

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    def test_add_new_table(self, qtbot, model_config):
        """
        Tests that a new table can be correctly added.
        """
        dialog = TablesDialog(model_config)
        dialog.show()

        table_list_widget = dialog.table_list_widget
        pages_widget = dialog.pages_widget
        qtbot.mouseClick(
            table_list_widget.add_button, Qt.MouseButton.LeftButton
        )
        # new name is random
        new_name = list(pages_widget.pages.keys())[-1]

        # Table model
        # the table is added to the model internal list
        assert new_name in table_list_widget.model.table_names
        # the table appears in the tables list on the left-hand side of the dialog
        new_model_index = table_list_widget.model.index(
            model_config.tables.count - 1, 0
        )
        assert new_model_index.data() == new_name
        # the item is selected
        assert table_list_widget.list.selectedIndexes()[0].data() == new_name

        # Page widget
        selected_page = pages_widget.currentWidget()
        assert new_name in selected_page.findChild(QLabel).text()
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        # button is disabled
        assert save_button.isEnabled() is False

        # the table is in the widgets list
        assert new_name in pages_widget.pages.keys()
        # the form page is selected
        assert selected_page == pages_widget.pages[new_name]
        # the form is filled with the name but with empty URL
        name_field: FormField = selected_page.findChild(FormField, "name")
        url_field: FormField = selected_page.findChild(FormField, "url")
        url_widget: TableUrlWidget = url_field.widget
        assert name_field.value() == new_name
        assert url_widget.line_edit.text() == ""

        # the model is updated
        assert model_config.has_changes is True
        assert model_config.tables.does_table_exist(new_name) is True
        assert model_config.tables.get_table_config_from_name(new_name) == {}

        # save with wrong URL (show error message)
        url_widget.line_edit.setText("wrong URL")
        assert save_button.isEnabled() is True
        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert "exist" in url_field.message.text()

        # save with empty URL (show error message)
        url_widget.line_edit.setText("")
        assert save_button.isEnabled() is True
        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert "empty" in url_field.message.text()

        # save with URL
        url_widget.line_edit.setText("files/table.csv")
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert url_field.message.text() == ""
        assert model_config.tables.get_table_config_from_name(new_name) == {
            "url": "files/table.csv"
        }

        # rename and save
        renamed_table_name = "A new shiny name"
        name_field.widget.setText(renamed_table_name)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert name_field.message.text() == ""

        # the page widget is renamed
        assert renamed_table_name in pages_widget.pages.keys()
        assert renamed_table_name in selected_page.findChild(QLabel).text()

        # model configuration
        assert model_config.tables.does_table_exist(new_name) is False
        assert model_config.tables.does_table_exist(renamed_table_name) is True
        assert model_config.tables.get_table_config_from_name(
            renamed_table_name
        ) == {"url": "files/table.csv"}

    def test_rename_table(self, qtbot, model_config):
        """
        Tests that a table is renamed correctly.
        """
        current_name = "Table 3"
        new_name = "Table X"
        dialog = TablesDialog(model_config, current_name)
        dialog.show()

        pages_widget = dialog.pages_widget
        selected_page = pages_widget.currentWidget()

        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        name_field: FormField = selected_page.findChild(FormField, "name")
        url_field: FormField = selected_page.findChild(FormField, "url")

        # Change the name and save
        assert name_field.value() == current_name
        name_field.widget.setText(new_name)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert name_field.message.text() == ""
        assert url_field.message.text() == ""

        # the page widget is renamed
        assert new_name in pages_widget.pages.keys()
        assert new_name in selected_page.findChild(QLabel).text()

        # model has changes
        assert model_config.has_changes is True
        assert model_config.tables.does_table_exist(current_name) is False
        assert model_config.tables.does_table_exist(new_name) is True
        assert model_config.tables.get_table_config_from_name(new_name) == {
            "url": "files\\table.csv",
            "index_col": ["Column 1"],
            "parse_dates": ["Column 1"],  # True converted to list
        }

        # set duplicated name
        name_field.widget.setText("Table 1")
        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert "already exists" in name_field.message.text()
        assert model_config.tables.names == [
            "Table 1",
            "Table 2",
            "Table 5",
            "Table 6",
            "Table 7",
            "Table 8",
            new_name,
        ]

    def test_delete_table(self, qtbot, model_config):
        """
        Tests that a table is deleted correctly.
        """
        dialog = TablesDialog(model_config)
        table_list_widget = dialog.table_list_widget
        pages_widget = dialog.pages_widget

        # select a table from the list
        deleted_table = "Table 2"
        model_index = table_list_widget.model.index(1, 0)
        assert model_index.data() == deleted_table
        table_list_widget.list.selectionModel().select(
            model_index, QItemSelectionModel.Select
        )

        # delete button is enabled and the item is selected
        assert table_list_widget.delete_button.isEnabled() is True
        assert (
            table_list_widget.list.selectedIndexes()[0].data() == deleted_table
        )

        # delete
        def confirm_deletion():
            widget = QApplication.activeModalWidget()
            qtbot.mouseClick(
                widget.findChild(QPushButton), Qt.MouseButton.LeftButton
            )

        QTimer.singleShot(100, confirm_deletion)
        qtbot.mouseClick(
            table_list_widget.delete_button, Qt.MouseButton.LeftButton
        )

        assert isinstance(pages_widget.currentWidget(), TableEmptyPageWidget)
        assert deleted_table not in pages_widget.pages.keys()
        assert model_config.tables.does_table_exist(deleted_table) is False
        assert deleted_table not in table_list_widget.model.table_names

    @pytest.mark.parametrize(
        "table_name, shown_fields, hidden_fields",
        [
            (
                "Table 3",
                csv_fields,
                excel_fields + h5_fields,
            ),
            (
                "Table 7",
                excel_fields,
                csv_fields + h5_fields,
            ),
            # parse_dates is hidden because it cannot be used
            (
                "Table 5",
                h5_fields,
                csv_fields + excel_fields + hidden_h5_fields,
            ),
            (
                "Table 2",
                [],
                csv_fields + excel_fields + h5_fields,
            ),
        ],
    )
    def test_field_visibility(
        self,
        qtbot,
        model_config,
        table_name,
        shown_fields,
        hidden_fields,
    ):
        """
        Tests that, when the file type changes, the fields for the appropriate file
        extensions are shown and the others hidden. Field visibility is handled by
        UrlWidget and empty QGroupBox are handles by TableUrlWidget.
        """
        dialog = TablesDialog(model_config, table_name)
        dialog.show()

        selected_page = dialog.pages_widget.currentWidget()

        assert selected_page.findChild(FormField, "name").value() == table_name

        # 1. the url field is enabled without errors or warnings
        url_field: FormField = selected_page.findChild(FormField, "url")
        url_widget: TableUrlWidget = url_field.widget
        assert url_field.widget.isEnabled() is True

        # force the dialog to be visible other isVisible always returns False
        dialog.show()

        # 2. the correct fields are shown or hidden
        for field_name in shown_fields:
            form_field: FormField = selected_page.findChild(
                FormField, field_name
            )
            assert form_field.isVisible() is True

        # 3. If all fields are hidden, check visibility of QGroupBox
        if not shown_fields:
            boxes: List[QGroupBox] = [
                selected_page.findChild(QGroupBox, box_name)
                for box_name in ["Parsing options", "Table configuration"]
            ]
            assert all([box.isHidden() for box in boxes])

        # 4. Set invalid file only for one scenario. Fields become invisible
        if table_name == "Table 3":
            url_widget.line_edit.setText("a")
            assert url_field.message.text() != ""
            assert url_widget.table is None
            for field_name in (
                self.csv_fields + self.excel_fields + self.h5_fields
            ):
                form_field: FormField = selected_page.findChild(
                    FormField, field_name
                )
                assert form_field.widget.isVisible() is False

    @pytest.mark.parametrize(
        "table_name",
        ["csv_table", "excel_file", "h5_table"],
    )
    def test_valid_table_file(self, qtbot, table_name):
        """
        Tests the dialog when a valid table is provided. This mainly tests the form
        validation; individual widgets are tested in the parameter dialog tests.
        """
        # use table from TableSelectorWidget
        model_config = ModelConfig(self.model_file_table_selector)
        dialog = TablesDialog(model_config, table_name)
        selected_page = dialog.pages_widget.currentWidget()
        url_field: FormField = selected_page.findChild(FormField, "url")
        # noinspection PyTypeChecker
        url_widget: TableUrlWidget = url_field.widget
        form = url_widget.form

        dialog.hide()

        assert form.find_field_by_name("name").value() == table_name

        # 1. the url field is without errors or warnings
        assert url_widget.isEnabled() is True
        assert url_field.message.text() == ""
        if "csv" in url_widget.full_file:
            assert url_widget.table.equals(pd.read_csv(url_widget.full_file))
        elif "h5" in url_widget.full_file:
            df, index_names = df_from_h5(url_widget.full_file, key="/flow")
            assert url_widget.table.equals(df)
            assert get_index_names(url_widget.table) == index_names
        else:
            assert url_widget.table.equals(pd.read_excel(url_widget.full_file))

        # 2. buttons are enabled
        assert url_widget.open_button.isEnabled() is True
        assert url_widget.reload_button.isEnabled() is True

        # 3. test validate method
        output = url_widget.validate("url", "Url", url_widget.get_value())
        assert output.validation is True

        # 4. test form validation - a valid dictionary is returned without error
        # message on the field skip other invalid fields
        form_data = form.validate()
        assert url_field.message.text() == ""

        assert isinstance(form_data, dict)
        assert form_data["name"] == table_name
        assert form_data["url"] == url_widget.get_value()

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

        fields = ["url"]
        model_table_dict = {}
        if url_widget.file_ext == ".csv":
            fields += ["index_col", "parse_dates"]
        elif url_widget.file_ext == ".xlsx":
            fields += ["index_col", "parse_dates", "sheet_name"]
        else:
            fields += ["key"]
        for f in fields:
            value = form.find_field_by_name(f).widget.get_value()
            # convert index_col to integer
            if f == "index_col" and table_name == "excel_file":
                all_cols = list(url_widget.table.columns)
                value = [all_cols.index(col_name) for col_name in value]
            if value:
                model_table_dict[f] = value

        assert (
            model_config.tables.get_table_config_from_name(table_name)
            == model_table_dict
        )

    def test_index_col_change_warning(self, qtbot, model_config):
        """
        Tests that, when the table indexes are changed, a warning is shown. This
        alerts the user that they may be breaking the configuration of parameters
        depending on the table.
        """
        table_name = "csv_table"
        model_config = ModelConfig(self.model_file_table_selector)
        dialog = TablesDialog(model_config, table_name)
        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyUnresolvedReferences
        url_widget: TableUrlWidget = selected_page.findChild(
            FormField, "url"
        ).widget
        index_col: FormField = selected_page.findChild(FormField, "index_col")
        index_col_widget: IndexColWidget = index_col.widget
        spy_index = QSignalSpy(url_widget.index_changed)

        # 2. save form
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        assert save_button.isEnabled() is False
        save_button.setEnabled(True)
        # button is enable
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        # 1. change index
        index_col_widget.combo_box.uncheck_all()
        index_col_widget.combo_box.check_items([0])
        assert spy_index.count() == 2

        # 2. save form
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        # button is enable
        assert save_button.isEnabled() is True

        QTimer.singleShot(100, partial(check_msg, "param_csv_file"))
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
