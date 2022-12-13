import pytest
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QGroupBox
from typing import List
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import (
    ColumnWidget,
    IndexWidget,
    SourceSelectorWidget,
    TableSelectorWidget,
    UrlWidget,
    FormField,
)
from pywr_editor.widgets import ComboBox
from pywr_editor.utils import default_index_name
from tests.utils import resolve_model_path

field_visibility = {
    "value": {
        "show": ["value"],
        "hide": [
            "index",
            "column",
            "table",
            "url",
            "index_col",
            "parse_dates",
        ],
    },
    "table": {
        "show": ["index", "column", "table"],
        "hide": ["url", "index_col", "parse_dates", "value"],
    },
    "anonymous_table": {
        "show": ["url", "index_col", "parse_dates", "index", "column"],
        "hide": ["value", "table"],
    },
    "dataframe_anonymous_table": {
        "show": ["url", "index_col", "parse_dates", "column"],
        "hide": ["table"],
    },
}

available_sources_param = [
    "An existing model table",
    "A table from an external file",
    "Provide value",
]
available_sources_df_param = [
    "An existing model table",
    "A table from an external file",
]


class TestDialogParameterSourceSelectorWidget:
    """
    Tests the SourceSelectorWidget in the parameter dialog. This is used to select the
    source of the parameter (table, url or value) or the source of the value of a
    parameter (for example the "threshold" attribute of a StorageThresholdParameter).
    """

    model_file = resolve_model_path("model_dialog_parameters.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "param_name, widget_items, shown_fields, hidden_fields",
        [
            # source is value
            (
                "param1",
                available_sources_param,
                field_visibility["value"]["show"],
                field_visibility["value"]["hide"],
            ),
            # source is table
            (
                "param_with_valid_csv_table",
                available_sources_param,
                field_visibility["table"]["show"],
                field_visibility["table"]["hide"],
            ),
            # source is anonymous table
            (
                "param_with_valid_anonymous_excel_table",
                available_sources_param,
                field_visibility["anonymous_table"]["show"],
                field_visibility["anonymous_table"]["hide"],
            ),
            # DataFrameParameter does not use "values" or "index"
            (
                "dataframe_param",
                available_sources_df_param,
                field_visibility["dataframe_anonymous_table"]["show"],
                field_visibility["dataframe_anonymous_table"]["hide"],
            ),
        ],
    )
    def test_field_visibility_init(
        self,
        qtbot,
        model_config,
        param_name,
        widget_items,
        shown_fields,
        hidden_fields,
    ):
        """
        Tests that some fields and the Configuration QGroupBox are shown or hidden
        based on the selected source type (value, external file or anonymous table)
        when the form is initialised.
        """
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.show()

        assert selected_page.findChild(FormField, "name").value() == param_name

        source_widget: SourceSelectorWidget = selected_page.findChild(
            FormField, "source"
        ).widget
        group_box: QGroupBox = selected_page.findChild(
            QGroupBox, "Table configuration"
        )

        # 1. Check widget items
        assert source_widget.combo_box.all_items == widget_items

        # 2. Check field visibility
        for field_name in shown_fields:
            form_field: FormField = selected_page.findChild(
                FormField, field_name
            )
            assert form_field.widget.isVisible() is True

        for field_name in hidden_fields:
            form_field: FormField = selected_page.findChild(
                FormField, field_name
            )
            assert form_field.widget.isVisible() is False

        # 1. The Configuration group and other fields are properly shown or hidden
        # based on the source
        if (
            param_name != "dataframe_param"
            and source_widget.get_value() == source_widget.labels["value"]
        ):
            assert group_box.isVisible() is False
        else:
            assert group_box.isVisible() is True

    def test_source_change_value_to_anonymous_table(self, qtbot, model_config):
        """
        Tests that, when the source changes from value to an anonymous table, the
        fields are properly hidden or shown and their values reset.
        """
        param_name = "param1"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.show()

        assert selected_page.findChild(FormField, "name").value() == param_name

        source_widget: SourceSelectorWidget = selected_page.findChild(
            FormField, "source"
        ).widget

        url_field: FormField = selected_page.findChild(FormField, "url")
        # noinspection PyTypeChecker
        url_widget: UrlWidget = url_field.widget
        # noinspection PyTypeChecker
        file_changed_spy = QSignalSpy(url_widget.file_changed)
        updated_table_spy = QSignalSpy(url_widget.updated_table)

        # 1. Change source from value to anonymous table (UrlWidget)
        source_widget.combo_box.setCurrentText(
            source_widget.labels["anonymous_table"]
        )

        # 2. Fields associated with UrlWidget are shown
        for field_name in field_visibility["anonymous_table"]["show"]:
            form_field: FormField = selected_page.findChild(
                FormField, field_name
            )
            assert form_field.widget.isVisible() is True

        # 3. Other fields are instead hidden
        for field_name in field_visibility["anonymous_table"]["hide"]:
            form_field: FormField = selected_page.findChild(
                FormField, field_name
            )
            assert form_field.widget.isVisible() is False

        # 4. Check UrlWidget
        # Signal not triggered (blocked)
        assert file_changed_spy.count() == 0
        # force table update
        assert updated_table_spy.count() == 1
        # field is reset/empty
        assert url_field.message.text() == ""
        assert url_widget.table is None
        assert url_widget.full_file is None
        assert url_widget.file_ext == ""

        # 5. Check other linked fields - url is empty so table is not available
        for name in ["column", "index_col", "parse_dates"]:
            widget: ColumnWidget = selected_page.findChild(
                FormField, name
            ).widget
            assert widget.combo_box.isEnabled() is False

            if name == "column":
                assert widget.combo_box.all_items == ["None"]
            else:
                # value set in line_edit
                assert widget.combo_box.all_items == []
            assert widget.combo_box.currentText() == "None"

        # disabled ComboBox for anonymous index
        index_widget: IndexWidget = selected_page.findChild(
            FormField, "index"
        ).widget
        combo_boxes: List[ComboBox] = index_widget.findChildren(ComboBox)
        assert len(combo_boxes) == 1
        assert combo_boxes[0].currentText() == ""
        assert combo_boxes[0].isEnabled() is False
        assert combo_boxes[0].objectName() == default_index_name

    def test_source_change_anonymous_table_to_table(self, qtbot, model_config):
        """
        Tests that, when the source changes from an anonymous table to a model table,
        the fields are properly hidden or shown and their values reset.
        """
        param_name = "param_with_valid_anonymous_excel_table"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.show()

        assert selected_page.findChild(FormField, "name").value() == param_name

        source_widget: SourceSelectorWidget = selected_page.findChild(
            FormField, "source"
        ).widget

        url_field: FormField = selected_page.findChild(FormField, "url")
        # noinspection PyTypeChecker
        url_widget: UrlWidget = url_field.widget
        table_field: FormField = selected_page.findChild(FormField, "table")
        # noinspection PyTypeChecker
        table_widget: TableSelectorWidget = table_field.widget
        table_updated_spy_url = QSignalSpy(url_widget.updated_table)
        table_updated_spy_table = QSignalSpy(table_widget.updated_table)

        # 1. Change source from value to table (TableSelectorWidget)
        source_widget.combo_box.setCurrentText(source_widget.labels["table"])

        # 2. Fields associated with TableSelectorWidget are shown
        for field_name in field_visibility["table"]["show"]:
            form_field: FormField = selected_page.findChild(
                FormField, field_name
            )
            assert form_field.widget.isVisible() is True

        # 3. Other fields are instead hidden
        for field_name in field_visibility["table"]["hide"]:
            form_field: FormField = selected_page.findChild(
                FormField, field_name
            )
            assert form_field.widget.isVisible() is False

        # 4. Signal triggered to reload table in TableSelectorWidget
        assert table_updated_spy_table.count() == 1
        # field is reset/empty
        assert table_field.message.text() == ""
        assert table_widget.table is None
        assert table_widget.combo_box.currentText() == "None"

        # 5. Check UrlWidget - this is always reset
        assert table_updated_spy_url.count() == 1
        # field is reset/empty
        assert url_field.message.text() == ""
        assert url_widget.table is None
        assert url_widget.full_file is None
        assert url_widget.file_ext == ""

    def test_multiple_changes(self, qtbot, model_config):
        """
        Tests the widget when the source is changed multiple times.
        """
        param_name = "param1"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.show()

        assert selected_page.findChild(FormField, "name").value() == param_name

        source_widget: SourceSelectorWidget = selected_page.findChild(
            FormField, "source"
        ).widget

        spy = {
            "url": QSignalSpy(
                selected_page.findChild(FormField, "url").widget.updated_table
            ),
            "table": QSignalSpy(
                selected_page.findChild(FormField, "table").widget.updated_table
            ),
        }

        for change_counter, name in enumerate(
            ["url", "value", "url", "table", "value"]
        ):
            field: FormField = selected_page.findChild(FormField, name)
            # noinspection PyTypeChecker
            widget = field.widget

            if name == "url":
                label = source_widget.labels["anonymous_table"]
            else:
                label = source_widget.labels[name]

            source_widget.combo_box.setCurrentText(label)

            # test widget content
            if name == "url":
                assert widget.isEnabled() is True
                assert widget.line_edit.text() == ""
            elif name == "table":
                assert widget.combo_box.isEnabled() is True
                assert widget.combo_box.currentText() == "None"
            else:
                assert widget.line_edit.text() == ""

            # test Signals
            if name in ["url", "table"]:
                assert widget.table is None
                assert spy[name].count() == change_counter + 1

    def test_param_wo_source(self, qtbot, model_config):
        param_name = "param_no_source"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.show()

        assert selected_page.findChild(FormField, "name").value() == param_name

        source_widget: SourceSelectorWidget = selected_page.findChild(
            FormField, "source"
        ).widget
        assert source_widget.get_value() == source_widget.labels["value"]
