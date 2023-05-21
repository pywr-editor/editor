import pytest
from PySide6.QtCore import QItemSelectionModel, QPoint, Qt
from PySide6.QtWidgets import QLabel

from pywr_editor.dialogs import NodeDialog
from pywr_editor.form import SlotsTableWidget
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestStorageSection:
    """
    Tests the MultiSplitLinkSection and StorageSection.
    """

    model_file = resolve_model_path("model_dialog_multi_split_link.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @staticmethod
    def set_text_in_cell(
        qtbot,
        widget: SlotsTableWidget,
        row: int,
        column: int,
        original_text: str,
        new_text: str,
    ) -> None:
        """
        Sets a text on the TableView of the SlotsTableWidget.
        :param qtbot: The qtbot instance.
        :param widget: The widget instance.
        :param row: The row index to alter.
        :param column: The column index to alter.
        :param original_text: The text in table.
        :param new_text: The new text to set.
        :return: None
        """
        table = widget.slot_table
        x = table.columnViewportPosition(column) + 5
        y = table.rowViewportPosition(row) + 10
        assert (
            widget.model.data(widget.model.index(row, column), Qt.DisplayRole)
            == original_text
        )

        qtbot.mouseClick(table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y))
        qtbot.mouseDClick(table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y))
        qtbot.keyClick(table.viewport().focusWidget(), Qt.Key_Backspace)
        for letter in list(new_text):
            if letter == " ":
                key = Qt.Key_Space
            elif letter == ".":
                key = Qt.Key_Period
            else:
                key = getattr(Qt, f"Key_{letter.title()}")
            qtbot.keyClick(table.viewport().focusWidget(), key)
        qtbot.keyClick(table.viewport().focusWidget(), Qt.Key_Enter)
        qtbot.wait(100)

        assert (
            widget.model.data(widget.model.index(row, column), Qt.DisplayRole)
            == new_text
        )

    @pytest.mark.parametrize(
        "node_name, target_nodes, edge_warning_message",
        [
            ("not_connected", [], "node must be connected to at least 2 nodes"),
            (
                "one_connection",
                ["Output"],
                "The extra slot created by this node is not connected",
            ),
        ],
    )
    def test_not_connected_node(
        self, qtbot, model_config, node_name, target_nodes, edge_warning_message
    ):
        """
        Tests the widget when the Multi Split Link is not connected or
        do not have enough edges.
        """
        dialog = NodeDialog(model_config=model_config, node_name=node_name)
        dialog.hide()

        form = dialog.form
        slots_field = form.find_field_by_name("slots_field")
        widget: SlotsTableWidget = slots_field.widget
        # noinspection PyTypeChecker
        edge_message_label: QLabel = widget.findChild(QLabel, "edge_warning_message")

        # 1. Check widget attributes
        assert widget.target_nodes == target_nodes
        assert widget.total_edges == len(target_nodes)
        assert widget.edge_slot_names == [None] * len(target_nodes)

        # key not provided, use defaults
        assert widget.total_extra_slots == 0
        assert widget.node_config_slot_names == []

        # 2. Check message and widget status
        assert edge_warning_message in edge_message_label.text()
        assert widget.slot_table.isEnabled() is False

        # 3. Check value and validation
        assert slots_field.value() is None
        # user can save other fields
        assert widget.validate("", "", "").validation is True

    @pytest.mark.parametrize(
        "node_name, edge_slot_names, node_slot_names, expected_value",
        [
            (
                "valid_wo_names",
                [0, 1],
                [0, 1],
                {
                    "extra_slots": 1,
                    "slot_names": [0, 1],
                    "target_nodes": ["Output", "Output2"],
                    "factors": None,
                },
            ),
            (
                "valid_w_names",
                ["wtw", "reservoir", "potato"],
                ["reservoir", "wtw", "potato"],
                {
                    "extra_slots": 2,
                    "slot_names": ["reservoir", "wtw", "potato"],
                    # sorted by slot name
                    "target_nodes": ["Output2", "Output", "Output3"],
                    "factors": [0.1, 2, None],
                },
            ),
            (
                "valid_partial_factors",
                [0, 1],
                [0, 1],
                {
                    "extra_slots": 1,
                    "slot_names": [0, 1],
                    "target_nodes": ["Output", "Output2"],
                    "factors": [0.1, None],
                },
            ),
        ],
    )
    def test_valid_node(
        self,
        qtbot,
        model_config,
        node_name,
        edge_slot_names,
        node_slot_names,
        expected_value,
    ):
        """
        Tests when the node is properly connected and all slots are defined.
        This also tests the validation of factors.
        """
        dialog = NodeDialog(model_config=model_config, node_name=node_name)
        dialog.hide()

        form = dialog.form
        slots_field = form.find_field_by_name("slots_field")
        widget: SlotsTableWidget = slots_field.widget
        table = widget.slot_table
        # noinspection PyTypeChecker
        edge_message_label: QLabel = widget.findChild(QLabel, "edge_warning_message")

        # 1. Check widget attributes
        unsorted_nodes = ["Output", "Output2"]
        if node_name == "valid_w_names":
            unsorted_nodes.append("Output3")
        assert widget.target_nodes == unsorted_nodes
        assert widget.total_edges == len(unsorted_nodes)
        # sorted based on target node
        assert widget.edge_slot_names == edge_slot_names
        assert widget.total_extra_slots == len(unsorted_nodes) - 1
        # sorted based on provided values in dictionary
        assert widget.node_config_slot_names == node_slot_names
        assert edge_message_label.text() == ""

        # 2. Check SlotTableModel
        assert table.isEnabled() is True
        assert widget.model.nodes == expected_value["target_nodes"]
        assert widget.model.slot_names == expected_value["slot_names"]
        factor_list = expected_value["factors"]
        if factor_list is None:
            factor_list = [None] * len(expected_value["target_nodes"])
        assert widget.model.factors == factor_list

        # 3. Check value and validation
        assert slots_field.value() == expected_value
        # user can save other fields
        assert widget.validate("", "", "").validation is True

        # 4. Test unpack_from_data_helper by validating form
        values = expected_value.copy()
        # removed on save
        del values["target_nodes"]
        if not values["factors"]:
            del values["factors"]
        assert form.validate() == {
            **{
                "name": node_name,
                # type is replaced on form save
                "type": "Multi split link",
                "nsteps": 2,
            },
            **values,
        }

        # check slot names in edges (not changed)
        for node, slot_name in zip(
            expected_value["target_nodes"], expected_value["slot_names"]
        ):
            assert model_config.edges.slot(node_name, node, 1) == slot_name
            assert model_config.edges.slot(node_name, node, 2) is None

        # 5. Change slot name and resend form
        new_slot_name = "my new slot name"
        self.set_text_in_cell(
            qtbot=qtbot,
            widget=widget,
            row=1,
            column=0,
            original_text=str(expected_value["slot_names"][1]),
            new_text=new_slot_name,
        )
        form.save_button.setEnabled(True)
        qtbot.mouseClick(form.save_button, Qt.MouseButton.LeftButton)

        # check node dictionary
        changed_node_idx = 1
        values["slot_names"][changed_node_idx] = new_slot_name
        assert model_config.nodes.config(node_name) == {
            **{
                "name": node_name,
                "type": "multisplitlink",
                "nsteps": 2,
            },
            **values,
        }

        # check slot in edges
        assert (
            model_config.edges.slot(node_name, expected_value["target_nodes"][0], 1)
            == expected_value["slot_names"][0]
        )
        assert (
            model_config.edges.slot(
                node_name, expected_value["target_nodes"][changed_node_idx], 1
            )
            == new_slot_name
        )

        # 6. Test when factors are changed in model and get_value() in widget
        if node_name == "valid_wo_names":
            self.set_text_in_cell(
                qtbot=qtbot,
                widget=widget,
                row=0,
                column=1,
                original_text="",
                new_text="6.0",
            )
            assert widget.get_value()["factors"] == [6, None]
            self.set_text_in_cell(
                qtbot=qtbot,
                widget=widget,
                row=1,
                column=1,
                original_text="",
                new_text="0.3",
            )
            assert widget.get_value()["factors"] == [6, 0.3]

            # set all empty to return None
            for i in range(2):
                self.set_text_in_cell(
                    qtbot=qtbot,
                    widget=widget,
                    row=i,
                    column=1,
                    original_text=str(widget.get_value()["factors"][i]),
                    new_text="",
                )
            assert widget.get_value()["factors"] is None

    @pytest.mark.parametrize(
        "node_name, warning_message, node_slot_names",
        [
            # total edges not matching slot_names
            (
                "slot_name_wrong_len",
                "The slot names are not properly configured for this node",
                # slots all empty
                {"Output": None, "Output2": None},
            ),
            # slot name in edge is None
            (
                "slot_name_not_provided_in_edge",
                "The slot names are not properly configured for this node",
                # slots all empty
                {"Output": None, "Output2": None},
            ),
            # slot name in edge does not matching slot_names
            (
                "slot_name_not_matching",
                "The slot named 'wtw', set in the configuration for",
                # sorting is followed, missing node added at the end
                # (they are sorted alphabetically because they come from a set)
                {"Output2": 0, "Output3": 5, "Output": None, "Output4": None},
            ),
        ],
    )
    def test_wrong_slot_names(
        self, qtbot, model_config, node_name, warning_message, node_slot_names
    ):
        """
        Tests when the wrong slot names are provided in the node dictionary or
        in the model edges.
        """
        dialog = NodeDialog(model_config=model_config, node_name=node_name)
        dialog.hide()

        form = dialog.form
        slots_field = form.find_field_by_name("slots_field")
        widget: SlotsTableWidget = slots_field.widget

        # 1. Check message
        assert warning_message in slots_field.message.text()

        # 2. Check TableWidget which is empty
        assert widget.slot_table.isEnabled() is True

        expected_slot_names = list(node_slot_names.keys())
        if node_name == "slot_name_not_matching":
            assert widget.model.nodes[0:2] == expected_slot_names[0:2]
            # sorting in set is not respected sometimes
            assert expected_slot_names[2] in widget.model.nodes
            assert expected_slot_names[3] in widget.model.nodes
        else:
            assert widget.model.nodes == expected_slot_names
        assert widget.model.slot_names == list(node_slot_names.values())
        assert widget.model.factors == [None] * len(node_slot_names)

        # 3. Check validation
        assert widget.validate("", "", "").validation is False

    def test_sorting(self, qtbot, model_config):
        """
        Tests row sorting when the Move up and Move down are pressed.
        """
        dialog = NodeDialog(model_config=model_config, node_name="valid_w_names")
        dialog.hide()

        form = dialog.form
        slots_field = form.find_field_by_name("slots_field")
        widget: SlotsTableWidget = slots_field.widget

        row_id = 1
        widget.slot_table.clearSelection()
        row = widget.model.index(row_id, 0)
        widget.slot_table.selectionModel().select(row, QItemSelectionModel.Select)

        qtbot.mouseClick(widget.move_down, Qt.MouseButton.LeftButton)
        assert widget.model.nodes == ["Output2", "Output3", "Output"]
        assert widget.model.slot_names == ["reservoir", "potato", "wtw"]
        assert widget.model.factors == [0.1, None, 2]
