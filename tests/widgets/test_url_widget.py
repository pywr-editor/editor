# from pathlib import Path

import pandas as pd
import pytest

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import (  # IndexColWidget,; UrlWidget,
    ColumnWidget,
    FormField,
    IndexWidget,
)
from pywr_editor.model import ModelConfig
from pywr_editor.utils import default_index_name
from pywr_editor.widgets import ComboBox
from tests.utils import resolve_model_path

# from PySide6.QtCore import Qt, QTimer
# from PySide6.QtTest import QSignalSpy
# from PySide6.QtWidgets import QLineEdit, QPushButton, QSpinBox


#


def df_from_h5(
    file: str, key: str, start: int = 0
) -> [pd.DataFrame, list[str]]:
    """
    Reads the DataFrame and reset the index.
    :param file: The H5 file.
    :param key: The store key.
    :param start: The starting table row. Default to 0.
    :return: The DataFrame and the index names in a tuple.
    """
    # noinspection PyTypeChecker
    df: pd.DataFrame = pd.read_hdf(file, key=key, start=start)
    index_names = list(df.index.names)
    if index_names != [None]:
        df.reset_index(inplace=True)
    else:
        index_names = [default_index_name]

    return df, index_names


class TestDialogParameterUrlWidget:
    """
    Tests the UrlWidget in the parameter dialog. This is used for anonymous tables
    only.
    """

    model_file = resolve_model_path("model_dialog_parameters_url_widget.json")
    common_fields = [
        "index",
        "column",
        "index_col",
        "parse_dates",
    ]
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

    @pytest.mark.parametrize(
        "param_name, shown_fields, hidden_fields",
        [
            (
                "param_csv_file",
                csv_fields + common_fields,
                excel_fields + h5_fields,
            ),
            (
                "param_excel_file",
                excel_fields + common_fields,
                csv_fields + h5_fields,
            ),
            # parse_dates is hidden because it cannot be used
            (
                "param_h5_file",
                h5_fields + list(set(common_fields) - set(hidden_h5_fields)),
                csv_fields + excel_fields + hidden_h5_fields,
            ),
            (
                "param_non_existing_file",
                [],
                csv_fields + excel_fields + h5_fields,
            ),
        ],
    )
    def test_field_visibility(
        self, qtbot, model_config, param_name, shown_fields, hidden_fields
    ):
        """
        Tests that, when the file type changes, the fields for the appropriate file
        extensions are shown and the others hidden.
        """
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()

        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. the url field is enabled without errors or warnings
        url_field: FormField = selected_page.findChild(FormField, "url")
        assert url_field.widget.isEnabled() is True

        # force the dialog to be visible other isVisible always returns False
        dialog.show()

        # 2. the correct fields are shown or hidden
        for field_name in shown_fields:
            form_field: FormField = selected_page.findChild(
                FormField, field_name
            )
            assert form_field.isVisible() is True

        for field_name in hidden_fields:
            form_field: FormField = selected_page.findChild(
                FormField, field_name
            )
            assert form_field.widget.isVisible() is False

        # 3. index and column fields are always visible. They are disabled when there
        # is an error
        index_widget: IndexWidget = selected_page.findChild(
            FormField, "index"
        ).widget
        for combo_box in index_widget.findChildren(ComboBox):
            # all fields are hidden, there is an error
            if not shown_fields:
                assert combo_box.isEnabled() is False
            else:
                assert combo_box.isEnabled() is True

        column_widget: ColumnWidget = selected_page.findChild(
            FormField, "column"
        ).widget
        if not shown_fields:
            assert column_widget.combo_box.isEnabled() is False
        else:
            assert column_widget.combo_box.isEnabled() is True

    # @pytest.mark.parametrize(


#         "param_name",
#         ["param_csv_file", "param_excel_file", "param_h5_file"],
#     )
#     def test_valid_table_file(self, qtbot, model_config, param_name):
#         dialog = ParametersDialog(model_config, param_name)
#         selected_page = dialog.pages_widget.currentWidget()
#         url_field: FormField = selected_page.findChild(FormField, "url")
#         # noinspection PyTypeChecker
#         url_widget: UrlWidget = url_field.widget
#         form = url_widget.form
#
#         dialog.show()
#
#         assert selected_page.findChild(FormField, "name").value() == param_name
#
#         # 1. the url field is enabled without errors or warnings
#         assert url_widget.isEnabled() is True
#         assert url_field.message.text() == ""
#         if "csv" in url_widget.full_file:
#             assert url_widget.table.equals(pd.read_csv(url_widget.full_file))
#         elif "h5" in url_widget.full_file:
#             df, index_names = df_from_h5(
#                 url_widget.full_file, key="/flow", start=1
#             )
#             assert url_widget.table.equals(df)
#             assert get_index_names(url_widget.table) == index_names
#         else:
#             assert url_widget.table.equals(pd.read_excel(url_widget.full_file))
#
#         # 2. buttons are enabled
#         assert url_widget.open_button.isEnabled() is True
#         assert url_widget.reload_button.isEnabled() is True
#
#         # 3. test validate method
#         output = url_widget.validate("url", "Url", url_widget.get_value())
#         assert output.validation is True
#
#         # 4. test form validation - a valid dictionary is returned without error
#         # message on the field skip other invalid fields
#         form_data = form.validate()
#         assert url_field.message.text() == ""
#
#         assert isinstance(form_data, dict)
#         assert form_data["name"] == param_name
#         assert form_data["type"] == "constant"
#         assert form_data["url"] == url_widget.get_value()
#
#         # 5. Save form to test filter
#         save_button: QPushButton = selected_page.findChild(
#             QPushButton, "save_button"
#         )
#         # enable button (disabled due to no changes)
#         assert model_config.has_changes is False
#         assert save_button.isEnabled() is False
#         save_button.setEnabled(True)
#         qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
#         assert model_config.has_changes is True
#
#         fields = ["url", "index", "column"]
#         model_param_dict = {"type": "constant"}
#         if url_widget.file_ext == ".csv":
#             fields += ["index_col", "parse_dates"]
#         elif url_widget.file_ext == ".xlsx":
#             fields += ["index_col", "parse_dates", "sheet_name"]
#         else:
#             fields += ["key"]
#             model_param_dict["start"] = form.find_field_by_name("start").value()
#         for f in fields:
#             value = form.find_field_by_name(f).widget.get_value()
#             # convert index_col to integer
#             if f == "index_col" and param_name == "param_excel_file":
#                 all_cols = list(url_widget.table.columns)
#                 value = [all_cols.index(col_name) for col_name in value]
#
#             if value:
#                 model_param_dict[f] = value
#
#         assert (
#             model_config.parameters.get_config_from_name(param_name)
#             == model_param_dict
#         )
#
#     @pytest.mark.parametrize(
#         "param_name, message",
#         [
#             ("param_non_existing_file", "The table file does not exist"),
#             ("param_file_ext_not_supported", "is not supported"),
#         ],
#     )
#     def test_invalid_table_file(self, qtbot, model_config, param_name, message):
#         """
#         Test the widget when the table file does not exist or is not supported.
#         """
#         dialog = ParametersDialog(model_config, param_name)
#         selected_page = dialog.pages_widget.currentWidget()
#         url_field: FormField = selected_page.findChild(FormField, "url")
#         # noinspection PyTypeChecker
#         url_widget: UrlWidget = url_field.widget
#         dialog.hide()
#
#         assert selected_page.findChild(FormField, "name").value() == param_name
#
#         # 1. the url field is enabled but with errors or warnings
#         assert url_widget.isEnabled() is True
#         assert message in url_field.message.text()
#         assert url_widget.table is None
#
#         # 2. check buttons status
#         assert url_widget.open_button.isEnabled() is False
#         # reload button is always enabled in case the file gets created
#         assert url_widget.reload_button.isEnabled() is True
#
#         # 3. test validate method
#         output = url_widget.validate("url", "Url", url_widget.get_value())
#         assert output.validation is False
#         assert "The file must exist" in output.error_message
#
#         # 4. test form validation - False is returned with an error message set on the
#         # field
#         QTimer.singleShot(100, close_message_box)
#         form_data = url_widget.form.validate()
#         assert form_data is False
#         assert "The file must exist" in url_field.message.text()
#
#     def test_file_changed_signal(self, qtbot, model_config):
#         """
#         Checks that, when the file changes, the file_changed Signal is triggered. The
#         Signal calls the on_reload_all_data and on_update_file methods.
#         """
#         param_name = "param_csv_file"
#         dialog = ParametersDialog(model_config, param_name)
#         selected_page = dialog.pages_widget.currentWidget()
#         url_field: FormField = selected_page.findChild(FormField, "url")
#         # noinspection PyTypeChecker
#         url_widget: UrlWidget = url_field.widget
#         dialog.hide()
#
#         # 1. Init signal spy
#         # noinspection PyTypeChecker
#         spy = QSignalSpy(url_widget.file_changed)
#         assert selected_page.findChild(FormField, "name").value() == param_name
#         assert spy.isValid() is True
#         assert spy.count() == 0
#
#         # 2. check that Signal is emitted and values are updated when relative path
#         # is set
#         rel_new_file = "files/table.xlsx"
#         abs_new_file = str(model_path() / rel_new_file)
#         url_widget.line_edit.setText(rel_new_file)
#         assert spy.count() == 1
#         assert (
#             url_widget.get_value() == rel_new_file
#         )  # relative path to JSON file
#         assert url_widget.full_file == abs_new_file
#         assert url_widget.file_ext == ".xlsx"
#
#         # 3. check that Signal is emitted and values are updated when absolute path
#         # is set
#         url_widget.line_edit.setText(abs_new_file)
#         # signal is still triggered only once after changing the line_edit text
#         assert spy.count() == 2
#         # this is set to relative to model path
#         assert Path(url_widget.get_value()) == Path(rel_new_file)
#         assert url_widget.full_file == abs_new_file
#         assert url_widget.file_ext == ".xlsx"
#
#     def test_force_table_update(self, qtbot, model_config):
#         """
#         Checks that, when one of the fields needed to parse the table file is changed,
#         the changed widget triggers the on_table_reload Slot of the UrlWidget.
#         """
#         param_name = "param_csv_file"
#         dialog = ParametersDialog(model_config, param_name)
#         selected_page = dialog.pages_widget.currentWidget()
#         url_field: FormField = selected_page.findChild(FormField, "url")
#         # noinspection PyTypeChecker
#         url_widget: UrlWidget = url_field.widget
#         dialog.hide()
#
#         assert selected_page.findChild(FormField, "name").value() == param_name
#
#         for field_name in url_widget.force_table_update:
#             widget = selected_page.findChild(FormField, field_name).widget
#             if isinstance(widget, QLineEdit):
#                 # noinspection PyTypeChecker
#                 spy = QSignalSpy(widget.textChanged)
#                 widget.setText(";")
#             elif isinstance(widget, QSpinBox):
#                 # noinspection PyTypeChecker
#                 spy = QSignalSpy(widget.textChanged)
#                 widget.setValue(3)
#             elif isinstance(widget, ComboBox):
#                 # noinspection PyUnresolvedReferences
#                 spy = QSignalSpy(widget.currentIndexChanged)
#                 # set index different from default value
#                 value = widget.currentIndex()
#                 if value == 0:
#                     widget.setCurrentIndex(1)
#                 else:
#                     widget.setCurrentIndex(0)
#             else:
#                 # ignore custom widget, these are tested in their own test files
#                 continue
#
#             # individual Signal is triggered only once for each widget instance
#             assert spy.count() == 1
#
#     def test_register_updated_table(self, qtbot, model_config):
#         """
#         Checks that, when the table changes, the IndexColWidget and ParseDatesWidget
#         fields are properly updated.
#         """
#         param_name = "param_csv_file"
#         dialog = ParametersDialog(model_config, param_name)
#         selected_page = dialog.pages_widget.currentWidget()
#         url_field: FormField = selected_page.findChild(FormField, "url")
#         # noinspection PyTypeChecker
#         url_widget: UrlWidget = url_field.widget
#         spy = QSignalSpy(url_widget.updated_table)
#         dialog.hide()
#
#         assert selected_page.findChild(FormField, "name").value() == param_name
#
#         # trigger table update by reloading the data
#         qtbot.mouseClick(url_widget.reload_button, Qt.MouseButton.LeftButton)
#         assert spy.count() == 1
#
#     def test_index_changed(self, qtbot, model_config):
#         """
#         Test that, when a new index on the table is set, the IndexWidget and
#         ColumnWidget are updated.
#         """
#         param_name = "param_csv_file"
#         dialog = ParametersDialog(model_config, param_name)
#         selected_page = dialog.pages_widget.currentWidget()
#         url_field: FormField = selected_page.findChild(FormField, "url")
#         # noinspection PyTypeChecker
#         url_widget: UrlWidget = url_field.widget
#         spy = QSignalSpy(url_widget.index_changed)
#         dialog.hide()
#
#         # trigger index_changed Signal by selecting Column 3
#         index_col_widget: IndexColWidget = selected_page.findChild(
#             FormField, "index_col"
#         ).widget
#         index_col_widget.combo_box.check_items(2)
#
#         assert spy.count() == 1
#
#         # check that the ColumnWidget is updated
#         index_widget: ColumnWidget = selected_page.findChild(
#             FormField, "column"
#         ).widget
#         assert index_widget.combo_box.all_items == [
#             "None",
#             " Date",
#         ]
#
#     def test_reset(self, qtbot, model_config):
#         """
#         Tests the reset method.
#         """
#         param_name = "param_csv_file"
#         dialog = ParametersDialog(model_config, param_name)
#         selected_page = dialog.pages_widget.currentWidget()
#         url_field: FormField = selected_page.findChild(FormField, "url")
#         # noinspection PyTypeChecker
#         url_widget: UrlWidget = url_field.widget
#         spy = QSignalSpy(url_widget.updated_table)
#         dialog.hide()
#
#         url_widget.reset()
#
#         assert spy.count() == 1
#         # field is reset/empty
#         assert url_field.message.text() == ""
#         assert url_widget.isEnabled() is True
#         assert url_widget.table is None
#         assert url_widget.full_file is None
#         assert url_widget.file_ext == ""
#
#     def test_parse_error_h5(self, qtbot, model_config):
#         """
#         Tests that, when the file cannot be parsed (for example when a data store does
#         not have any key), the field is disabled with a warning message and the other
#         fields are shown to let user change the parser options.
#         """
#         selected_parameter = "param_with_h5_no_keys"
#         dialog = ParametersDialog(model_config, selected_parameter)
#         dialog.show()
#
#         selected_page = dialog.pages_widget.currentWidget()
#         key_field: FormField = selected_page.findChild(FormField, "key")
#         url_field: FormField = selected_page.findChild(FormField, "url")
#         # noinspection PyTypeChecker
#         url_widget: UrlWidget = url_field.widget
#
#         assert (
#             selected_page.findChild(FormField, "name").value()
#             == selected_parameter
#         )
#         assert "Cannot parse the file" in url_field.message.text()
#         assert (
#             key_field.message.text() == "The H5 file does not contain any key"
#         )
#
#         # H5 and common fields are visible
#         for field_name in self.h5_fields + list(
#             set(self.common_fields) - set(self.hidden_h5_fields)
#         ):
#             shown_field: FormField = selected_page.findChild(
#                 FormField, field_name
#             )
#             assert shown_field.isVisible() is True
#
#             # table is not available. Index_col is always disabled, key is disabled
#             # because no keys are available
#             if field_name in ["index", "column", "index_col", "key"]:
#                 if field_name != "index":
#                     assert shown_field.widget.combo_box.isEnabled() is False
#                 else:
#                     assert all(
#                         [
#                             f.isEnabled() is False
#                             for f in shown_field.findChildren(ComboBox)
#                         ]
#                     )
#             else:
#                 assert shown_field.isEnabled() is True
#
#             # warning message on key field
#             if field_name == "key":
#                 assert "does not contain" in shown_field.message.text()
#
#         # 3. test validate method
#         output = url_widget.validate("url", "Url", url_widget.get_value())
#         assert output.validation is False
#         assert "The file must exist" in output.error_message
#
#         # 4. test form validation - False is returned with an error message set on
#         # the field
#         QTimer.singleShot(100, close_message_box)
#         form_data = url_widget.form.validate()
#         assert form_data is False
#         assert "The file must exist" in url_field.message.text()
