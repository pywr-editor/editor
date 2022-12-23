from functools import partial

import pytest
from PySide6.QtCore import Qt, QTimer

from pywr_editor.dialogs import EdgeSlotsDialog
from pywr_editor.dialogs.slots.edge_slots_widget import EdgeSlotsWidget
from pywr_editor.model import ModelConfig
from tests.utils import change_table_view_cell, check_msg, resolve_model_path


class TestSlotsDialog:
    """
    Tests the dialog with the widget to handle nodes' slots.
    """

    model_file = resolve_model_path("model_dialog_slots.json")

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    @pytest.fixture()
    def widget(self, model_config) -> EdgeSlotsWidget:
        """
        Returns the EdgeSlotsWidget instance.
        :param model_config: The ModelConfig instance.
        :return: The EdgeSlotsWidget instance.
        """
        dialog = EdgeSlotsDialog(model_config)
        dialog.hide()

        # noinspection PyTypeChecker
        return dialog.findChild(EdgeSlotsWidget)

    def test_init(self, qtbot, model_config, widget):
        """
        Tests that all the nodes and slots are listed.
        """
        model = widget.model
        for ei, edge in enumerate(model_config.edges.get_all()):
            assert model.data(model.index(ei, 0), Qt.DisplayRole) == edge[0]
            assert model.data(model.index(ei, 1), Qt.DisplayRole) == edge[1]
            # slots
            if len(edge) >= 3 and edge[2] is not None:
                assert model.data(model.index(ei, 2), Qt.DisplayRole) == str(
                    edge[2]
                )
            else:
                assert model.data(model.index(ei, 2), Qt.DisplayRole) == ""
            if len(edge) == 4 and edge[3] is not None:
                assert model.data(model.index(ei, 3), Qt.DisplayRole) == str(
                    edge[3]
                )
            else:
                assert model.data(model.index(ei, 3), Qt.DisplayRole) == ""

    def test_edit_slot_name_from_empty(self, qtbot, model_config, widget):
        """
        Adds a new name when slot is empty.
        """
        new_name = "reservoir"
        change_table_view_cell(
            qtbot=qtbot,
            table=widget.table,
            row=0,
            column=2,
            old_name="",
            new_name=new_name,
        )
        assert model_config.edges.get_all()[0][2] == new_name

    def test_remove_slot_name(self, qtbot, model_config, widget):
        """
        Removes a slot name.
        """
        change_table_view_cell(
            qtbot=qtbot,
            table=widget.table,
            row=2,
            column=3,
            old_name="2",
            new_name="",
        )
        assert model_config.edges.get_all()[2] == ["Node C", "Node D"]

    def test_rename_existing_slot(self, qtbot, model_config, widget):
        """
        Renames an existing slot.
        """
        new_name = "input"
        change_table_view_cell(
            qtbot=qtbot,
            table=widget.table,
            row=1,
            column=2,
            old_name="1",
            new_name=new_name,
        )
        assert model_config.edges.get_all()[1][2] == new_name

    @pytest.mark.parametrize(
        "old_name, new_name",
        [
            # with slot_names
            ("slot2", "slot_xyz"),
            # with slot_names to integer
            ("slot2", 1),
        ],
    )
    def test_rename_slot_for_multi_split_link(
        self, qtbot, model_config, widget, old_name, new_name
    ):
        """
        Renames the slot for a MultiSplitLink.
        """
        change_table_view_cell(
            qtbot=qtbot,
            table=widget.table,
            row=6,
            column=2,
            old_name=old_name,
            new_name=new_name,
        )
        assert model_config.edges.get_all()[6][2] == new_name
        assert model_config.nodes.get_node_config_from_name("MultiSplitLink")[
            "slot_names"
        ] == ["slot1", "slot3", new_name]

    def test_rename_slot_for_multi_split_link_no_change(
        self, qtbot, model_config, widget
    ):
        """
        Checks when the slot is not renamed for a MultiSplitLink.
        """
        # 1. w/o slot_names - not renamed
        new_name = "slot_t"
        change_table_view_cell(
            qtbot=qtbot,
            table=widget.table,
            row=8,
            column=2,
            old_name="",
            new_name=new_name,
        )
        assert model_config.edges.get_all()[8][2] == new_name
        assert model_config.nodes.get_node_config_from_name(
            "MultiSplitLink - no slots"
        )["slot_names"] == ["slot1", "slot3"]

        # 2. Remove slot - error
        QTimer.singleShot(
            100,
            partial(check_msg, "The slot name for the 'MultiSplitLink' node"),
        )
        change_table_view_cell(
            qtbot=qtbot,
            table=widget.table,
            row=6,
            column=2,
            old_name="slot2",
            new_name="",
        )
        assert model_config.edges.get_all()[6][2] == "slot2"
        assert model_config.nodes.get_node_config_from_name("MultiSplitLink")[
            "slot_names"
        ] == ["slot1", "slot3", "slot2"]
