import pytest
from PySide6.QtTest import QSignalSpy
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import ParametersDialog
from pywr_editor.form import ParseDatesWidget, FormField
from tests.utils import resolve_model_path


class TestDialogParameterParseDatesWidget:
    """
    Tests the ParseDatesWidget in the parameter dialog. This only tests that, when the
    selected columns are changed, the table index does not get updated. Otherwise,
    the widget behaves like the IndexColWidget.
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

    def test_parse_dates_change(self, qtbot, model_config):
        """
        Tests that, when the columns with dates are changed, the field is correctly
        updated.
        """
        param_name = "param_with_index_col_list_of_str"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        parse_dates_widget: ParseDatesWidget = selected_page.findChild(
            FormField, "parse_dates"
        ).widget
        combo_box = parse_dates_widget.combo_box

        spy = QSignalSpy(combo_box.model().dataChanged)
        assert selected_page.findChild(FormField, "name").value() == param_name
        assert parse_dates_widget.get_value() == ["Column 2"]
        assert spy.count() == 0

        # 1. De-select all the columns
        # widget updates via dataChanged in model when user clicks on a checkbox.
        # Mock this.
        combo_box.uncheck_all()
        assert spy.count() == 1
        assert combo_box.checked_items() == []
        assert parse_dates_widget.get_value() == []
        assert parse_dates_widget.combo_box.lineEdit().text() == "None"

        # 2. Select new columns
        # Slot is triggered only once
        selected = ["Column 3", "Column 4"]
        selected_indexes = [
            combo_box.all_items.index(col_name) for col_name in selected
        ]
        combo_box.check_items(selected_indexes)

        # check Slot and values
        assert spy.count() == 2
        assert combo_box.checked_items() == selected
        assert parse_dates_widget.get_value() == selected
        assert parse_dates_widget.combo_box.lineEdit().text() == ", ".join(
            selected
        )

    def test_parse_dates_true(self, qtbot, model_config):
        """
        Tests that, when parse_dates is True, the widget uses the columns set as index
        (in the "index_col" key).
        """
        param_name = "param_with_parse_dates_true"
        dialog = ParametersDialog(model_config, param_name)
        selected_page = dialog.pages_widget.currentWidget()
        dialog.hide()

        parse_dates_widget: ParseDatesWidget = selected_page.findChild(
            FormField, "parse_dates"
        ).widget

        assert selected_page.findChild(FormField, "name").value() == param_name
        assert parse_dates_widget.get_value() == ["Column 1", "Column 4"]
