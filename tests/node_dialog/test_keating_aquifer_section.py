from functools import partial

import pytest
from PySide6.QtCore import QPoint, Qt, QTimer

from pywr_editor.dialogs import NodeDialog
from pywr_editor.form import (
    FloatWidget,
    KeatingStreamsWidget,
    TableValuesWidget,
)
from pywr_editor.model import ModelConfig
from tests.utils import (
    change_table_view_cell,
    check_msg,
    close_message_box,
    resolve_model_path,
)


class TestKeatingAquiferSection:
    """
    Tests the KeatingAquiferSection and KeatingStreamsWidget.
    """

    model_file = resolve_model_path(
        "model_dialog_node_keating_aquifer_section.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    def test_valid_node(
        self,
        qtbot,
        model_config,
    ):
        """
        Tests when valid data are passed to the widget.
        """
        dialog = NodeDialog(model_config=model_config, node_name="valid")
        dialog.hide()

        expected_levels = [[100, 200, 600], [1, 3, 6]]
        expected_transmissivity = [19, 1, 2]

        form = dialog.form
        save_button = form.save_button
        field = form.find_field_by_name("stream_flows")
        widget: KeatingStreamsWidget = field.widget
        model = widget.model

        # 1. Check model
        assert field.message.text() == ""
        assert model.levels == expected_levels
        assert model.transmissivity == expected_transmissivity

        for row_id in range(len(expected_levels) + 1):
            for col_id in range(len(expected_transmissivity)):
                model_value = model.data(
                    model.index(row_id, col_id), Qt.DisplayRole
                )
                # transmissivity row
                if row_id == len(expected_levels):
                    assert model_value == str(
                        expected_transmissivity[col_id]
                    ), (
                        f"Expected transmissivity: {expected_transmissivity[col_id]}, "
                        + f"got {model_value}"
                    )
                # level row
                else:
                    assert model_value == str(
                        expected_levels[row_id][col_id]
                    ), (
                        f"Expected level: {expected_levels[row_id][col_id]}, got "
                        + f"{model_value}"
                    )

        # 2. Check get_value and validate methods
        assert widget.get_value() == {
            "num_streams": 2,
            "stream_flow_levels": model.levels,
            "transmissivity": model.transmissivity,
        }
        assert widget.validate("", "", None).validation is True

        # check section filter
        assert form.validate() == {
            "name": "valid",
            # this is the QLineEdit value removed at form save
            "type": "Keating aquifer",
            "num_streams": 2,
            "stream_flow_levels": [[100, 200, 600], [1, 3, 6]],
            "transmissivity": [19, 1, 2],
            "coefficient": 1.0,
            "levels": [0.0, 1.0],
            "volumes": [0.0, 1.0],
        }

        # 3. Remove one level; validation must fail
        assert save_button.isEnabled() is False
        row, col = 1, 1
        change_table_view_cell(
            qtbot=qtbot,
            table=widget.table,
            row=row,
            column=col,
            old_name=str(model.levels[row][col]),
            new_name="",
        )
        assert save_button.isEnabled() is True

        # check model
        assert model.data(model.index(row, col), Qt.DisplayRole) == ""
        assert model.levels[row][col] is None

        # validate
        out = widget.validate("", "", None)
        assert out.validation is False
        assert (
            out.error_message
            == "You must provide all the levels for each stream"
        )

        # 4. Add level and remove one coefficient; validation must fail
        change_table_view_cell(
            qtbot=qtbot,
            table=widget.table,
            row=row,
            column=col,
            old_name="",
            new_name="99",
        )
        assert model.data(model.index(row, col), Qt.DisplayRole) == "99.0"
        assert model.levels[row][col] == 99

        row, col = 2, 0
        change_table_view_cell(
            qtbot=qtbot,
            table=widget.table,
            row=row,
            column=col,
            old_name=str(model.transmissivity[col]),
            new_name="",
        )

        # check model
        assert model.data(model.index(row, col), Qt.DisplayRole) == ""
        assert model.transmissivity[col] is None

        # validate
        out = widget.validate("", "", None)
        assert out.validation is False
        assert (
            out.error_message
            == "You must provide all the transmissivity coefficients for each level"
        )

        # 5. Reset widget and validate
        model.levels = []
        model.transmissivity = []
        out = widget.validate("", "", None)
        assert out.validation is False
        assert (
            "must provide at least one stream with a valid" in out.error_message
        )

    @pytest.mark.parametrize(
        "node_name, init_message",
        [
            ("invalid_empty_levels", None),
            ("invalid_empty_transmissivity", None),
            # check types
            ("invalid_type_transmissivity", "transmissivity must be a list"),
            (
                "invalid_type_transmissivity_not_number",
                "transmissivity must be a list",
            ),
            ("invalid_type_level", "levels must be a list of lists"),
            ("invalid_type_level_not_list", "must be a list of numbers"),
            (
                "invalid_type_level_not_number",
                "must be a list of numbers",
            ),
            ("invalid_level_wrong_size", "must hve the same number of levels"),
            (
                "invalid_level_transmissivity_size",
                "number of transmissivity coefficients must match",
            ),
        ],
    )
    def test_invalid_node(self, qtbot, model_config, node_name, init_message):
        """
        Tests when the configuration of the node is invalid.
        """
        dialog = NodeDialog(model_config=model_config, node_name=node_name)
        dialog.hide()

        field = dialog.form.find_field_by_name("stream_flows")
        widget: KeatingStreamsWidget = field.widget

        # model is empty
        assert widget.model.levels == []
        assert widget.model.transmissivity == []

        # check init message
        if init_message:
            assert init_message in field.message.text()
        else:
            assert field.message.text() == ""

        # validation fails
        out = widget.validate("", "", None)
        assert out.validation is False

    def test_add_delete_stream(self, qtbot, model_config):
        """
        Tests the add and delete stream buttons.
        """
        dialog = NodeDialog(model_config=model_config, node_name="valid")
        dialog.hide()

        form = dialog.form
        widget: KeatingStreamsWidget = form.find_field_by_name(
            "stream_flows"
        ).widget
        table = widget.table
        model = widget.model
        expected_levels = [[100, 200, 600], [1, 3, 6]]

        # 1. Add a new stream
        qtbot.mouseClick(widget.add_stream_button, Qt.MouseButton.LeftButton)
        expected_levels.append([None] * len(model.transmissivity))
        assert model.levels == expected_levels

        # 2. Select last row - button remains disabled
        assert widget.delete_stream_button.isEnabled() is False
        x = table.columnViewportPosition(1) + 5
        y = table.rowViewportPosition(model.rowCount() - 1) + 10
        qtbot.mouseClick(
            table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
        )
        assert widget.delete_stream_button.isEnabled() is False

        # 3. Delete stream
        row = 0
        # select row
        x = table.columnViewportPosition(1) + 5
        y = table.rowViewportPosition(row) + 10
        qtbot.mouseClick(
            table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
        )

        # delete
        assert widget.delete_stream_button.isEnabled() is True
        qtbot.mouseClick(widget.delete_stream_button, Qt.MouseButton.LeftButton)

        # check data
        del expected_levels[row]
        assert model.levels == expected_levels

        # 3. Delete last stream - disabled button gets disabled afterwards
        row = model.rowCount() - 2
        # select row
        x = table.columnViewportPosition(1) + 5
        y = table.rowViewportPosition(row) + 10
        qtbot.mouseClick(
            table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
        )

        # delete
        assert widget.delete_stream_button.isEnabled() is True
        qtbot.mouseClick(widget.delete_stream_button, Qt.MouseButton.LeftButton)
        assert widget.delete_stream_button.isEnabled() is False

        # check data
        del expected_levels[row]
        assert model.levels == expected_levels

    def test_add_delete_level(self, qtbot, model_config):
        """
        Tests the add and delete level buttons.
        """
        dialog = NodeDialog(model_config=model_config, node_name="valid")
        dialog.hide()

        form = dialog.form
        widget: KeatingStreamsWidget = form.find_field_by_name(
            "stream_flows"
        ).widget
        table = widget.table
        model = widget.model

        # 1. Add a new level
        qtbot.mouseClick(widget.add_level_button, Qt.MouseButton.LeftButton)
        assert model.levels == [[100, 200, 600, None], [1, 3, 6, None]]
        assert model.transmissivity == [19, 1, 2, None]

        # 2. Delete 2nd level
        column = 1
        # select row
        x = table.columnViewportPosition(column) + 5
        y = table.rowViewportPosition(0) + 10
        qtbot.mouseClick(
            table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
        )

        # delete
        assert widget.delete_level_button.isEnabled() is True
        qtbot.mouseClick(widget.delete_level_button, Qt.MouseButton.LeftButton)

        # check data
        assert model.levels == [[100, 600, None], [1, 6, None]]
        assert model.transmissivity == [19, 2, None]

    def test_volumes_validation(self, qtbot, model_config):
        """
        Tests the validation for the volumes field.
        """
        dialog = NodeDialog(model_config=model_config, node_name="valid")
        dialog.hide()

        form = dialog.form
        save_button = form.save_button
        levels_widget: TableValuesWidget = form.find_field_by_name(
            "levels"
        ).widget
        volumes_widget: TableValuesWidget = form.find_field_by_name(
            "volumes"
        ).widget

        # set the levels
        levels_widget.model.values[0] = [100, 200, 300]
        save_button.setEnabled(True)

        # 1. Set wrong number of volumes
        volumes_widget.model.values[0] = [5, 6]
        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert (
            "number of volumes (2) must match"
            in volumes_widget.form_field.message.text()
        )

        # 2. Set correct number of volumes
        volumes_widget.model.values[0].append(8)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert volumes_widget.form_field.message.text() == ""

    def test_storativity_validation(self, qtbot, model_config):
        """
        Tests the storativity for the volumes field.
        """
        dialog = NodeDialog(model_config=model_config, node_name="valid")
        dialog.hide()

        form = dialog.form
        save_button = form.save_button
        levels_widget: TableValuesWidget = form.find_field_by_name(
            "levels"
        ).widget
        storativity_widget: TableValuesWidget = form.find_field_by_name(
            "storativity"
        ).widget
        volumes_widget: TableValuesWidget = form.find_field_by_name(
            "volumes"
        ).widget
        area_widget: FloatWidget = form.find_field_by_name("area").widget

        # set the levels
        levels_widget.model.values[0] = [100, 200, 300]
        area_widget.line_edit.setText("10")
        volumes_widget.model.values = [[]]
        save_button.setEnabled(True)

        # 1. Set wrong number of factors
        storativity_widget.model.values[0] = [5, 6, 8]
        QTimer.singleShot(100, close_message_box)
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert (
            "number of factors (3) must match"
            in storativity_widget.form_field.message.text()
        )

        # 2. Set correct number of factors
        del storativity_widget.model.values[0][0]
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert storativity_widget.form_field.message.text() == ""

    @pytest.mark.parametrize(
        "storativity, volumes, area, error_message",
        [
            # set no volumes or storativity - at least one is needed
            (
                None,
                None,
                None,
                "must provide either the volumes or the storativity",
            ),
            # set both
            ([1, 2], [3, 6, 7], 123, "but not both values at the same time"),
            # set storativity w/o area
            ([1, 2], None, None, "the aquifer area is mandatory"),
        ],
    )
    def test_section_validation(
        self, qtbot, model_config, storativity, volumes, area, error_message
    ):
        """
        Tests the section validation.
        """
        dialog = NodeDialog(model_config=model_config, node_name="valid_empty")
        dialog.hide()

        form = dialog.form
        save_button = form.save_button
        storativity_widget: TableValuesWidget = form.find_field_by_name(
            "storativity"
        ).widget
        volumes_widget: TableValuesWidget = form.find_field_by_name(
            "volumes"
        ).widget
        area_widget: FloatWidget = form.find_field_by_name("area").widget

        if area:
            area_widget.line_edit.setText(str(area))
        if volumes:
            volumes_widget.model.values = [volumes]
        if storativity:
            storativity_widget.model.values = [storativity]
        save_button.setEnabled(True)

        QTimer.singleShot(100, partial(check_msg, error_message))
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
