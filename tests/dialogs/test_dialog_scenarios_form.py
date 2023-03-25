import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QLineEdit, QPushButton

from pywr_editor.dialogs import ScenariosDialog
from pywr_editor.dialogs.scenarios.scenario_options_widget import (
    ScenarioOptionsWidget,
)
from pywr_editor.form import FormField
from pywr_editor.model import ModelConfig
from pywr_editor.widgets import SpinBox
from tests.utils import change_table_view_cell, resolve_model_path


class TestScenariosDialog:
    """
    Tests the scenario form and its widgets.
    """

    model_file = resolve_model_path("model_dialog_scenario_form.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.mark.parametrize(
        "scenario_name, expected_options, expected_scenario_dict",
        [
            (
                "valid_complete",
                {"ensemble_names": ["First", "Second"], "slice": None},
                {
                    "name": "valid_complete",
                    "size": 2,
                    "ensemble_names": ["First", "Second"],
                },
            ),
            (
                "valid_wo_names",
                {"ensemble_names": [], "slice": None},
                {"name": "valid_wo_names", "size": 2},
            ),
            (
                "valid_names_empty",
                {"ensemble_names": [], "slice": None},
                {"name": "valid_names_empty", "size": 2},
            ),
            (
                "valid_w_slice",
                {"ensemble_names": [], "slice": [0, 3]},
                {"name": "valid_w_slice", "size": 5, "slice": [0, 3]},
            ),
            # when all ensemble index are given in slice, slice returns None
            # because by default pywr runs all ensembles
            (
                "valid_all_slice",
                {"ensemble_names": [], "slice": None},
                {"name": "valid_all_slice", "size": 3},
            ),
        ],
    )
    def test_valid_init(
        self,
        qtbot,
        model_config,
        scenario_name,
        expected_options,
        expected_scenario_dict: dict,
    ):
        """
        Tests that the values are loaded correctly.
        """
        dialog = ScenariosDialog(model_config, scenario_name)
        dialog.show()

        selected_page = dialog.pages.currentWidget()
        # noinspection PyTypeChecker
        options_widget: ScenarioOptionsWidget = selected_page.findChild(
            ScenarioOptionsWidget
        )

        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value() == scenario_name
        )

        # 1. Check for initial warnings
        for form_field in selected_page.findChildren(FormField):
            form_field: FormField
            assert form_field.message.text() == ""
            if form_field.name == "options":
                assert form_field.value() == expected_options

        # 2. Validate options widget
        # remove one name and validation fails
        if scenario_name == "valid_complete":
            # no names are provided, validation does not fail
            out = options_widget.validate("", "", None)
            assert out.validation is True

            # emulate QTableView and its model
            options_widget.model.names = ["First", ""]
            out = options_widget.validate("", "", {})
            assert "you must provide the names for all the" in out.error_message

            # change for form submission
            options_widget.model.names = ["First", "Third"]
            expected_scenario_dict[
                "ensemble_names"
            ] = options_widget.model.names
        # no slice is provided, validation does not fail
        elif scenario_name == "valid_names_empty":
            out = options_widget.validate("", "", {})
            assert out.validation is True
        # de-select all slices and validation fails and test rename
        elif scenario_name == "valid_w_slice":
            # slice is provided, validation does not fail
            out = options_widget.validate("", "", {})
            assert out.validation is True

            # emulate QTableView and its model
            options_widget.model.slice = []
            out = options_widget.validate("", "", {})
            assert "must select at least a scenario" in out.error_message

            # change for form submission
            options_widget.model.slice = [0, 1]
            expected_scenario_dict["slice"] = [0, 1]

            # rename scenario
            new_name = "A new scenario name"
            # noinspection PyTypeChecker
            name: FormField = selected_page.findChild(FormField, "name")
            # noinspection PyTypeChecker
            name_line_edit: QLineEdit = name.findChild(QLineEdit)
            name_line_edit.setText(new_name)

            scenario_name = new_name
            expected_scenario_dict["name"] = new_name
        # if names are not provided, validation does not fail
        elif scenario_name == "valid_wo_names":
            out = options_widget.validate("", "", {})
            assert out.validation is True

        # 3. Enable submit button and send form for validation to test on_save method
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        assert (
            model_config.scenarios.get_config_from_name(scenario_name)
            == expected_scenario_dict
        )

        # 4. Test reset
        options_widget.reset()
        assert options_widget.model.names == []
        assert options_widget.model.slice == list(
            range(expected_scenario_dict["size"] + 1)
        )

    @pytest.mark.parametrize(
        "scenario_name, init_message",
        [
            # slice
            (
                "invalid_wrong_slice_type",
                "is not a valid list of",
            ),
            ("invalid_slice_not_int", "is not a valid list of"),
            ("invalid_wrong_slice_max_item", "slice item is larger than"),
            ("invalid_wrong_slice_size", "slice length (3) is larger than"),
            # ensemble names
            ("invalid_names_type", "must be a valid list of strings"),
            ("invalid_names_not_str", "must be a valid list of strings"),
            ("invalid_names_with_None", "must be a valid list of strings"),
            (
                "invalid_names_partial_length",
                "number of ensemble names (2)",
            ),
            # combined messages
            (
                "invalid_names_and_slice",
                ["item is larger than the", "number of ensemble names (2)"],
            ),
        ],
    )
    def test_invalid(self, qtbot, model_config, scenario_name, init_message):
        """
        Tests the widget when an invalid configuration is used.
        """
        dialog = ScenariosDialog(model_config, scenario_name)
        dialog.show()

        selected_page = dialog.pages.currentWidget()

        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value() == scenario_name
        )

        # 1. Check for initial warnings
        # noinspection PyTypeChecker
        option_field: FormField = dialog.findChild(FormField, "options")
        if isinstance(init_message, str):
            assert init_message in option_field.message.text()
        else:
            for sub_message in init_message:
                assert sub_message in option_field.message.text()

        # 2. Check widget value
        assert option_field.value() == {"ensemble_names": [], "slice": None}

        # 3. Enable submit button and send form for validation to test on_save method
        # noinspection PyTypeChecker
        save_button: QPushButton = selected_page.findChild(
            QPushButton, "save_button"
        )
        save_button.setEnabled(True)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        assert model_config.has_changes is True
        scenario_dict = model_config.scenarios.get_config_from_name(
            scenario_name
        )

        assert model_config.scenarios.get_config_from_name(scenario_name) == {
            "name": scenario_name,
            "size": scenario_dict["size"],
        }

    def test_action_buttons(self, qtbot, model_config):
        """
        Tests the widget action buttons to toggle checkboxes and reset names.
        """
        scenario_name = "valid_complete"
        dialog = ScenariosDialog(model_config, scenario_name)
        dialog.hide()

        selected_page = dialog.pages.currentWidget()

        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value() == scenario_name
        )

        # noinspection PyTypeChecker
        option_widget: ScenarioOptionsWidget = dialog.findChild(
            ScenarioOptionsWidget
        )

        # remove names
        button_tested = 0
        for button in option_widget.findChildren(QPushButton):
            if button.text() == "Reset names":
                qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
                assert option_widget.model.names == ["", ""]
                assert option_widget.get_value()["ensemble_names"] == []
                button_tested += 1
            elif button.text() == "Check all":
                qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
                values = list(range(0, option_widget.model.total_rows))
                assert option_widget.model.slice == values
                assert option_widget.get_value()["slice"] is None
                button_tested += 1
            elif button.text() == "Uncheck all":
                qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
                values = []
                assert option_widget.model.slice == values
                assert option_widget.get_value()["slice"] == values
                button_tested += 1

        assert button_tested == 3

    def test_slice_in_table_model(self, qtbot, model_config):
        """
        Checks that the slice list in the model is correctly updated.
        """
        dialog = ScenariosDialog(model_config, "valid_w_slice")
        dialog.hide()

        selected_page = dialog.pages.currentWidget()

        # noinspection PyTypeChecker
        options_widget: ScenarioOptionsWidget = selected_page.findChild(
            ScenarioOptionsWidget
        )
        table = options_widget.table
        model = options_widget.model

        x = table.columnViewportPosition(2) + 5

        # Uncheck 1
        dialog.show()
        y = table.rowViewportPosition(0) + 10

        qtbot.mouseClick(
            table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
        )
        assert model.slice == [3]

        # Uncheck all
        y = table.rowViewportPosition(3) + 10
        qtbot.mouseClick(
            table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
        )
        assert model.slice == []

        # Check one at the time
        new_values = []
        for r in range(4, -1, -1):
            y = table.rowViewportPosition(r) + 10
            qtbot.mouseClick(
                table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
            )
            new_values.append(r)
            assert model.slice == new_values

    @pytest.mark.parametrize(
        "scenario_name, ensemble_names",
        [
            ("valid_complete", ["First", "Second"]),
            # check model with empty name list (model must receive name list of same
            # size of scenario)
            ("valid_wo_names", ["", ""]),
        ],
    )
    def test_names_in_table_model(
        self, qtbot, model_config, scenario_name, ensemble_names
    ):
        """
        Checks that the names list in the model is correctly updated.
        """
        dialog = ScenariosDialog(model_config, scenario_name)
        dialog.hide()

        selected_page = dialog.pages.currentWidget()

        # noinspection PyTypeChecker
        options_widget: ScenarioOptionsWidget = selected_page.findChild(
            ScenarioOptionsWidget
        )
        table = options_widget.table
        model = options_widget.model

        x = table.columnViewportPosition(1) + 5

        # Empty name 1
        change_table_view_cell(
            qtbot=qtbot,
            table=table,
            row=0,
            column=1,
            old_name=ensemble_names[0],
            new_name="",
        )
        assert model.names == ["", model.names[1]]

        # Empty all
        change_table_view_cell(
            qtbot=qtbot,
            table=table,
            row=1,
            column=1,
            old_name=ensemble_names[1],
            new_name="",
        )
        assert model.names == ["", ""]

        # Fill one name at the time
        new_values = ["", ""]
        for r in range(2):
            y = table.rowViewportPosition(r) + 10
            qtbot.mouseClick(
                table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
            )
            qtbot.mouseDClick(
                table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
            )
            qtbot.keyClick(table.viewport().focusWidget(), Qt.Key_X)
            qtbot.keyClick(table.viewport().focusWidget(), Qt.Key_Enter)
            new_values[r] = "x"
            qtbot.wait(100)
            assert model.names == new_values

    def test_change_scenario_size(
        self,
        qtbot,
        model_config,
    ):
        """
        Tests that the model is updated when the scenario size is changed.
        New rows are added or removed from the table.
        """
        scenario_name = "valid_complete"
        dialog = ScenariosDialog(model_config, scenario_name)
        dialog.hide()

        selected_page = dialog.pages.currentWidget()
        # noinspection PyTypeChecker
        options_widget: ScenarioOptionsWidget = selected_page.findChild(
            ScenarioOptionsWidget
        )
        # noinspection PyTypeChecker
        size_widget: SpinBox = selected_page.findChild(SpinBox)

        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value() == scenario_name
        )

        or_size = size_widget.value()

        # increase size by 1
        size_widget.setValue(or_size + 1)
        assert options_widget.model.names == ["First", "Second", ""]
        assert options_widget.model.slice == [0, 1, 2]

        # increase size by 2
        size_widget.setValue(or_size + 2)
        assert options_widget.model.names == ["First", "Second", "", ""]
        assert options_widget.model.slice == [0, 1, 2, 3]

        # set it to 8
        size_widget.setValue(8)
        assert options_widget.model.names == [
            "First",
            "Second",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
        assert options_widget.model.slice == list(range(0, 8))

        # set name
        table = options_widget.table
        x = table.columnViewportPosition(1) + 5
        y = table.rowViewportPosition(4) + 10
        qtbot.mouseClick(
            table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
        )
        qtbot.mouseDClick(
            table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
        )
        qtbot.keyClick(table.viewport().focusWidget(), Qt.Key_X)
        qtbot.keyClick(table.viewport().focusWidget(), Qt.Key_Enter)
        qtbot.wait(100)

        # uncheck ensemble
        x = table.columnViewportPosition(2) + 5
        y = table.rowViewportPosition(4) + 10
        qtbot.mouseClick(
            table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
        )

        # decrease it to 6
        size_widget.setValue(6)
        assert options_widget.model.names == [
            "First",
            "Second",
            "",
            "",
            "x",
            "",
        ]
        assert options_widget.model.slice == [0, 1, 2, 3, 5]

        # decrease it by 1
        size_widget.setValue(5)
        assert options_widget.model.names == ["First", "Second", "", "", "x"]
        assert options_widget.model.slice == [0, 1, 2, 3]

        # decrease it by 1
        size_widget.setValue(4)
        assert options_widget.model.names == ["First", "Second", "", ""]
        assert options_widget.model.slice == list(range(0, 4))
