import pytest
from PySide6.QtCore import QTimer

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import (
    FormField,
    H5KeyWidget,
    IndexColWidget,
    ParseDatesWidget,
    UrlWidget,
)
from pywr_editor.model import ModelConfig
from pywr_editor.utils import get_index_names
from tests.utils import close_message_box, resolve_model_path
from tests.widgets.test_url_widget import df_from_h5


class TestDialogParameterH5KeyWidget:
    """
    Tests the H5KeyWidget in the parameter dialog. This applies to anonymous tables
    of H5 type only.
    """

    model_file = resolve_model_path("model_dialog_parameters_sheet_h5key.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """

        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, keys, selected_key",
        [
            (
                "param_with_valid_h5_table_w_index",
                ["/empty_table", "/flow", "/other", "/people"],
                "/flow",
            ),
            (
                "param_with_valid_h5_table_anonymous_index",
                ["/flow", "/rainfall"],
                "/flow",
            ),
        ],
    )
    def test_h5_key(self, qtbot, model_config, param_name, keys, selected_key):
        """
        Tests that the url and key widgets behave correctly when a H5 file is set using
        an anonymous table.
        """
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        key_field: FormField = selected_page.findChild(FormField, "key")
        # noinspection PyTypeChecker
        key_widget: H5KeyWidget = key_field.widget
        # noinspection PyUnresolvedReferences
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. the table is properly loaded w/o index
        assert url_widget.file_ext == ".h5"
        df, index_names = df_from_h5(url_widget.full_file, key=key_widget.value)
        assert url_widget.table.equals(df)
        assert get_index_names(url_widget.table) == index_names

        # 2. available keys and selected key is correctly set
        assert key_field.value() == selected_key
        assert key_field.message.text() == ""
        assert key_widget.combo_box.all_items == keys

        # 3. index_col field is disabled, parse_dates is not
        # noinspection PyUnresolvedReferences
        index_col_widget: IndexColWidget = selected_page.findChild(
            FormField, "index_col"
        ).widget
        # noinspection PyUnresolvedReferences
        parse_dates_widget: ParseDatesWidget = selected_page.findChild(
            FormField, "parse_dates"
        ).widget
        form = index_col_widget.form
        assert index_col_widget.isEnabled() is False
        assert parse_dates_widget.isEnabled() is True

        # 4. test validate method
        output = key_widget.validate("key", "Key", key_widget.get_value())
        assert output.validation is True

        # 5. test form validation - a valid dictionary is returned without error
        # message on the field skip other invalid fields
        QTimer.singleShot(100, close_message_box)

        form_data = form.validate()
        assert key_field.message.text() == ""

        assert isinstance(form_data, dict)
        assert "source" not in form_data
        assert form_data["name"] == param_name
        assert form_data["type"] == "constant"
        assert form_data["url"] == url_widget.get_value()
        assert form_data["key"] == key_widget.get_value()

    def test_change_key(self, qtbot, model_config):
        """
        Tests that, when the key or the table file changes, the table is reloaded.
        """
        param_name = "param_with_valid_h5_table_w_index"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        key_field: FormField = selected_page.findChild(FormField, "key")
        # noinspection PyTypeChecker
        key_widget: H5KeyWidget = key_field.widget
        # noinspection PyUnresolvedReferences
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget
        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. changing the selected key, reloads the table (Signal acts on text changes)
        new_key = "/other"
        key_widget.combo_box.setCurrentText(new_key)
        assert key_field.value() == new_key
        assert key_field.message.text() == ""
        new_df, new_index_names = df_from_h5(
            url_widget.full_file, key=key_widget.value
        )
        assert url_widget.table.equals(new_df)
        assert get_index_names(url_widget.table) == new_index_names

        # 2. set non-existing file, then set same H5 file. Table must be reloaded
        # and same key selected
        original_file = url_widget.full_file
        url_widget.line_edit.setText(original_file[0:-1])
        assert "not exist" in url_widget.form_field.message.text()
        # File does not exist and table is invalid
        assert url_widget.full_file is None
        assert url_widget.file_ext == ".h"
        assert url_widget.table is None

        # The sheet widget is disabled, empty and still visible
        assert key_widget.isEnabled() is False
        assert key_widget.combo_box.all_items == []
        assert key_widget.combo_box.currentText() == ""

        # Set original value - last key is selected
        url_widget.line_edit.setText(original_file)
        assert url_widget.form_field.message.text() == ""
        assert url_widget.full_file == original_file
        assert url_widget.file_ext == ".h5"
        assert url_widget.table.equals(new_df)
        assert get_index_names(url_widget.table) == new_index_names

        # 3. Load a new H5 file. Table must be reloaded and first key selected
        url_widget.line_edit.setText(r"files/table2.h5")
        assert url_widget.form_field.message.text() == ""
        assert url_widget.file_ext == ".h5"
        first_key = "/new_key"
        df, index_names = df_from_h5(url_widget.full_file, key=first_key)
        assert url_widget.table.equals(df)
        assert get_index_names(url_widget.table) == index_names

        assert key_widget.isEnabled() is True
        assert key_widget.combo_box.all_items == [first_key]
        assert key_widget.combo_box.currentText() == first_key
        assert key_widget.value == first_key

    def test_h5_non_existing_key(self, qtbot, model_config):
        """
        Tests that, when a non-existing key is provided, the first key is selected and
        a warning message is shown.
        """
        selected_parameter = "param_with_h5_table_wrong_key"
        dialog = ParametersDialog(model_config, selected_parameter)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        key_field: FormField = selected_page.findChild(FormField, "key")
        # noinspection PyTypeChecker
        key_widget: H5KeyWidget = key_field.widget
        # noinspection PyUnresolvedReferences
        url_widget: UrlWidget = selected_page.findChild(FormField, "url").widget
        first_key = "/empty_table"

        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value()
            == selected_parameter
        )
        assert "does not exist in the H5 file" in key_field.message.text()

        # 1. the first key is selected
        assert key_field.value() == first_key
        # 2. check table in first key
        df, index_names = df_from_h5(url_widget.full_file, key=first_key)
        assert url_widget.table.equals(df)
        assert get_index_names(url_widget.table) == index_names

        # 3. test validate method - validation passes because first key is selected
        output = key_widget.validate("key", "Key", key_widget.get_value())
        assert output.validation is True

    def test_h5_no_keys(self, qtbot, model_config):
        """
        Tests widget when a file with no keys is provided
        """
        selected_parameter = "param_with_h5_no_keys"
        dialog = ParametersDialog(model_config, selected_parameter)
        dialog.hide()

        selected_page = dialog.pages_widget.currentWidget()
        # noinspection PyTypeChecker
        key_field: FormField = selected_page.findChild(FormField, "key")
        # noinspection PyTypeChecker
        key_widget: H5KeyWidget = key_field.widget

        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value()
            == selected_parameter
        )
        assert (
            key_field.message.text() == "The H5 file does not contain any key"
        )

        # 1. field is disabled
        assert key_widget.isEnabled() is False
        assert key_widget.combo_box.all_items == []

        # 2. test validate method - validation fails
        output = key_widget.validate("key", "Key", key_widget.get_value())
        assert output.validation is False

        # 3. test form validation
        QTimer.singleShot(100, close_message_box)

        form_data = key_widget.form.validate()
        assert form_data is False
        assert key_field.message.text() != ""
