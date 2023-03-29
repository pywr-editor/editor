from functools import partial

import pandas as pd
import pytest
import win32com.client
from PySide6.QtCore import QItemSelection, QItemSelectionModel, Qt, QTimer
from PySide6.QtWidgets import QPushButton, QWidget

from pywr_editor.form import FormField, ParameterForm, TableValuesWidget
from pywr_editor.model import ModelConfig, ParameterConfig
from pywr_editor.utils import is_excel_installed
from tests.utils import check_msg, model_path


class TestDialogParameterTableValuesWidget:
    """
    Tests the TableValuesWidget.
    """

    default_values = {
        "x": list(range(0, 5)),
        "y": list(range(5, 10)),
    }

    @staticmethod
    def widget(
        value: dict[str, list[int | float]] | None,
        field_args: dict | None = None,
    ) -> TableValuesWidget:
        """
        Initialises the form and returns the widget.
        :param value: A dictionary containing the variable names as key and their
        values as values.
        :param field_args: Additional field arguments to pass to the widget.
        :return: An instance of TableValuesWidget.
        """
        # mock widgets
        form = ParameterForm(
            model_config=ModelConfig(),
            parameter_obj=ParameterConfig({}),
            available_fields={
                "Section": [
                    {
                        "name": "tabular_values",
                        "field_type": TableValuesWidget,
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

        table_field = form.find_field_by_name("tabular_values")
        return table_field.widget

    @pytest.mark.parametrize(
        "values, field_args",
        [
            ({"x": list(range(0, 8)), "y": list(range(5, 13))}, None),
            (
                {"x": list(range(0, 8)), "y": list(range(5, 13))},
                {"show_row_numbers": True},
            ),
        ],
    )
    def test_model(self, qtbot, values, field_args):
        """
        Tests the model.
        """
        table_widget = self.widget(value=values, field_args=field_args)
        model = table_widget.model

        # check counters
        show_row_numbers = True if field_args is not None else False
        assert model.rowCount() == len(values["x"])
        if show_row_numbers:
            assert model.columnCount() == len(values) + 1
        else:
            assert model.columnCount() == len(values)

        rows = range(0, model.rowCount())
        first_col = 0
        second_col = 1
        # check first column
        if show_row_numbers:
            assert [
                model.data(model.index(r, 0), Qt.DisplayRole) for r in rows
            ] == list(range(1, model.rowCount() + 1))
            assert model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "Row"
            first_col += 1
            second_col += 1

        # check data
        all_keys = list(values.keys())
        assert [
            model.data(model.index(r, first_col), Qt.DisplayRole) for r in rows
        ] == values["x"]
        assert [
            model.data(model.index(r, second_col), Qt.DisplayRole) for r in rows
        ] == values["y"]

        # check data header
        assert (
            model.headerData(first_col, Qt.Horizontal, Qt.DisplayRole)
            == all_keys[0].title()
        )
        assert (
            model.headerData(second_col, Qt.Horizontal, Qt.DisplayRole)
            == all_keys[1].title()
        )

        # set data
        model.setData(model.index(2, first_col), -999, Qt.EditRole)
        assert model.values[0][2] == -999
        model.setData(model.index(5, second_col), 444, Qt.EditRole)
        assert model.values[1][5] == 444

    @pytest.mark.parametrize(
        "values, field_args",
        [
            ({"x": list(range(0, 5)), "y": list(range(5, 10))}, None),
            (
                {
                    "x": list(range(0, 5)),
                    "y": list(range(5, 10)),
                    "z": list(range(15, 20)),
                },
                None,
            ),
            ({"x": [], "y": []}, None),
            ({"x": None, "y": None}, None),
            # test min values requirement
            (
                {"x": list(range(0, 5)), "y": list(range(5, 10))},
                {"min_total_values": 3},
            ),
            # test exact size of values requirement
            (
                {"x": list(range(0, 5)), "y": list(range(5, 10))},
                {"exact_total_values": 5},
            ),
            # test integers only
            (
                {"x": list(range(0, 2)), "y": list(range(0, 2))},
                {"use_integers_only": True},
            ),
            # test bounds
            (
                {"x": list(range(0, 5)), "y": list(range(0, 5))},
                {"enforce_bounds": True, "lower_bound": 0, "upper_bound": 10},
            ),
        ],
    )
    def test_valid(self, qtbot, values, field_args):
        """
        Tests that the field is loaded correctly.
        """
        table_widget = self.widget(value=values, field_args=field_args)
        table_field: FormField = table_widget.form_field

        assert table_field.message.text() == ""
        out = table_widget.validate("", "", table_widget.get_value())

        # 1. Check table and validate
        assert table_widget.model.rowCount() == (
            len(values["x"]) if values["x"] else 0
        )
        assert table_widget.model.columnCount() == len(values)
        assert table_widget.model.labels == list(values.keys())

        if values["x"] is None:
            assert table_widget.get_value() == {"x": [], "y": []}
        else:
            assert table_widget.get_value() == values
        assert out.validation is True

        # 2. Test reset
        table_widget.reset()
        new_values = {name: [] for name in values.keys()}
        assert table_widget.get_value() == new_values
        assert table_widget.model.values == [[] for _ in values.keys()]

    @pytest.mark.parametrize(
        "values, init_message, validation_message, expected_value, field_args",
        [
            # wrong type, table not filled, validation passes because values are
            # optional
            (
                {"x": 5, "y": list(range(5, 10))},
                "be all valid lists",
                None,
                {"x": [], "y": []},
                None,
            ),
            # lists must have same size, table is filled and padded with zeros
            (
                {"x": [5], "y": [1, 2, 3]},
                "number of values must be the same for each variable",
                None,
                {"x": [5, 0, 0], "y": [1, 2, 3]},
                None,
            ),
            # size of x is too small, table is filled
            (
                {"x": [5], "y": [1, 2, 3]},
                "number of values must be the same for each variable",
                "must provide at least 4 values",
                {"x": [5, 0, 0], "y": [1, 2, 3]},
                {"min_total_values": 4},
            ),
            # list with invalid types
            (
                {"x": [5, 2, True]},
                "can only contain numbers",
                "must provide at least 2 values",
                {"x": []},
                {"min_total_values": 2},
            ),
            # size of x does not match exact_total_values
            (
                {"x": [5, 5, 1], "y": [1, 2, 3]},
                "data points must exactly be 4",
                "provide exactly 4",
                {"x": [5, 5, 1], "y": [1, 2, 3]},
                {"exact_total_values": 4},
            ),
            # no warning at init but failure at validation
            (
                {"x": [], "y": []},
                None,
                "provide exactly 5",
                {"x": [], "y": []},
                {"exact_total_values": 5},
            ),
            # wrong type, empty table and validation passes
            (
                {"x": [[5, 2, 6]]},
                "can only contain numbers",
                None,
                {"x": []},
                None,
            ),
            # min_total_values set
            (
                {"x": [5, 2, 0]},
                "must be at least 20",
                "must provide at least 20",
                {"x": [5, 2, 0]},
                {"min_total_values": 20},
            ),
            # min_total_values set - multiple variables
            (
                {"x": [5, 2, 0], "y": [1, 2, 3]},
                "must be at least 20",
                "must provide at least 20",
                {"x": [5, 2, 0], "y": [1, 2, 3]},
                {"min_total_values": 20},
            ),
            # integers only - field is empty
            (
                {"x": [5.1, 0.2], "y": [99.12, 2, 3]},
                "can only contain integers",
                None,
                {"x": [], "y": []},
                {"use_integers_only": True},
            ),
            # values are outside bounds
            (
                {"x": list(range(0, 5)), "y": list(range(0, 5))},
                "are outside the allowed range",
                None,
                {"x": [], "y": []},
                {"enforce_bounds": True, "lower_bound": 0, "upper_bound": 2},
            ),
        ],
    )
    def test_invalid(
        self,
        qtbot,
        values,
        init_message,
        validation_message,
        expected_value,
        field_args,
    ):
        """
        Tests that the form displays a warning message when the provided value is
        invalid.
        """
        table_widget = self.widget(value=values, field_args=field_args)
        table_field: FormField = table_widget.form_field

        if init_message is None:
            assert table_field.message.text() == ""
        else:
            assert init_message in table_field.message.text()
        assert table_widget.get_value() == expected_value

        out = table_widget.validate("", "", table_widget.get_value())

        if validation_message is None:
            assert out.error_message is None
            assert out.validation is True
        # validation failed
        else:
            assert validation_message in out.error_message
            assert out.validation is False

    def test_add_new_row(self, qtbot):
        """
        Checks that the widget works properly when a new row is added.
        """
        table_widget = self.widget(
            value=self.default_values,
        )

        # add two more rows
        for d in range(1, 3):
            qtbot.mouseClick(table_widget.add_button, Qt.MouseButton.LeftButton)
            new_values = table_widget.get_value()

            assert new_values["x"][-1] == 0
            assert new_values["y"][-1] == 0
            assert len(new_values["x"]) == len(self.default_values["x"]) + d

    def test_delete_rows(self, qtbot):
        """
        Checks that the widget works properly when one or more rows are deleted.
        """
        table_widget = self.widget(
            # x=[0, 1, 2, 3, 4] y = [5, 6, 7, 8, 9]
            value=self.default_values,
        )

        assert table_widget.delete_button.isEnabled() is False

        # 1. Select one row and delete it
        row_idx = 2  # delete x=2 and y=7
        table_widget.table.setCurrentIndex(table_widget.model.index(row_idx, 0))
        assert table_widget.delete_button.isEnabled() is True
        qtbot.mouseClick(table_widget.delete_button, Qt.MouseButton.LeftButton)
        table_widget.table.clearSelection()

        # check row has been removed
        new_values = {}
        for name, value in self.default_values.items():
            value.pop(row_idx)
            new_values[name] = value
        assert table_widget.get_value() == new_values

        # 2. Delete multiple rows
        # select two rows - delete x=[0, 1] and y=[5, 6]
        selection = QItemSelection()
        for i in range(0, 2):
            idx = table_widget.model.index(i, 0)
            selection.select(idx, idx)

        # Apply the selection, using the row-wise mode.
        selection_model = table_widget.table.selectionModel()
        selection_model.select(selection, QItemSelectionModel.Select)

        # delete data and check result
        qtbot.mouseClick(table_widget.delete_button, Qt.MouseButton.LeftButton)

        new_values_2 = {}
        for name, value in new_values.items():
            new_values_2[name] = [
                v for vi, v in enumerate(value) if vi not in [0, 1]
            ]
        assert table_widget.get_value() == new_values_2

    def test_move_up(self, qtbot):
        """
        Checks that the widget works properly when one row is moved up
        """
        table_widget = self.widget(
            value=self.default_values,
        )

        assert table_widget.move_up.isEnabled() is False

        # 1. Select first row, button is still disabled
        row_idx = 0
        table_widget.table.setCurrentIndex(table_widget.model.index(row_idx, 0))
        assert table_widget.move_up.isEnabled() is False

        # 2. Select another row and move it
        row_idx = 2
        table_widget.table.setCurrentIndex(table_widget.model.index(row_idx, 0))
        assert table_widget.move_up.isEnabled() is True
        qtbot.mouseClick(table_widget.move_up, Qt.MouseButton.LeftButton)

        # check row has been moved
        new_values = {}
        for name, value in self.default_values.items():
            new_values[name] = (
                value[0 : row_idx - 1]
                + [value[row_idx]]
                + [value[row_idx - 1]]
                + value[row_idx + 1 :]
            )
        assert table_widget.get_value() == new_values

    def test_move_down(self, qtbot):
        """
        Checks that the widget works properly when one row is moved down
        """
        table_widget = self.widget(
            value=self.default_values,
        )

        assert table_widget.move_up.isEnabled() is False

        # 1. Select last row, button is still disabled
        row_idx = len(self.default_values["x"]) - 1
        table_widget.table.setCurrentIndex(table_widget.model.index(row_idx, 0))
        assert table_widget.move_down.isEnabled() is False

        # 2. Select another row and move it
        row_idx = 2
        table_widget.table.setCurrentIndex(table_widget.model.index(row_idx, 0))
        assert table_widget.move_down.isEnabled() is True
        qtbot.mouseClick(table_widget.move_down, Qt.MouseButton.LeftButton)

        # check row has been moved
        new_values = {}
        for name, value in self.default_values.items():
            new_values[name] = (
                value[0:row_idx]
                + [value[row_idx + 1]]
                + [value[row_idx]]
                + value[row_idx + 2 :]
            )
        assert table_widget.get_value() == new_values

    @pytest.mark.skipif(not is_excel_installed(), reason="requires Excel")
    def test_paste_from_excel(self, qtbot):
        """
        Tests the paste feature from Excel.
        """
        table_widget = self.widget(
            value=self.default_values,
        )

        assert table_widget.move_up.isEnabled() is False

        # copy spreadsheet data using VBA
        excel_file = str(model_path() / "files" / "monthly_profile_vba.xlsm")
        vba_module = "monthly_profile_vba.xlsm!MainModule"
        xl = win32com.client.Dispatch("Excel.Application")
        xl.Workbooks.Open(
            excel_file,
            ReadOnly=1,
        )

        # valid clipboard data
        xl.Application.Run(f"{vba_module}.CopyToClipboardTable2")
        table = pd.read_excel(excel_file, sheet_name="Table")
        new_values = {
            "x": list(table.iloc[:, 0].values),
            "y": list(table.iloc[:, 1].values),
        }
        qtbot.mouseClick(table_widget.paste_button, Qt.MouseButton.LeftButton)
        assert table_widget.get_value() == new_values

        # invalid data
        routines = [
            "CopyToClipboardTable",
            "CopyToClipboardAll",
        ]
        messages = [
            "must contain valid numbers",
            "must contain 2 columns",
        ]
        for routine, message in zip(routines, messages):
            xl.Application.Run(f"{vba_module}.{routine}")
            QTimer.singleShot(100, partial(check_msg, message))
            qtbot.mouseClick(
                table_widget.paste_button, Qt.MouseButton.LeftButton
            )
            assert table_widget.get_value() == new_values

        xl.Quit()
