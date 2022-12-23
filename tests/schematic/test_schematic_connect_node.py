from typing import Tuple

import pytest
from PySide6.QtCore import QPoint, Qt

from pywr_editor import MainWindow
from pywr_editor.schematic import Schematic, SchematicItem
from pywr_editor.toolbar.tab_panel import TabPanel
from tests.utils import resolve_model_path


class TestSchematicConnectNodes:
    model_file = resolve_model_path("model_delete_nodes.json")

    @pytest.fixture
    def init_window(self) -> Tuple[MainWindow, Schematic, TabPanel]:
        """
        Initialises the window.
        :return: A tuple with the window, schematic and tab panel instances.
        """
        window = MainWindow(self.model_file)
        window.hide()
        schematic = window.schematic
        node_op_panel = window.toolbar.tabs["Nodes"].panels["Operations"]

        return window, schematic, node_op_panel

    def test_connect_node(self, qtbot, init_window):
        """
        Tests when a node is connected to another one.
        """
        window, schematic, node_op_panel = init_window
        model_config = schematic.model_config

        # select Link3
        source_point = schematic.mapFromScene(QPoint(50, 500))
        qtbot.mouseMove(schematic, source_point, -1)
        qtbot.mouseClick(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.NoModifier,
            source_point,
        )
        found = False
        for node in schematic.items():
            if isinstance(node, SchematicItem) and node.name == "Link3":
                found = True
                assert node.isSelected() is True
        assert found is True

        # enable connect mode
        qtbot.mouseClick(
            node_op_panel.buttons["Connect"], Qt.MouseButton.LeftButton
        )

        # select the target node Reservoir
        target_point = schematic.mapFromScene(QPoint(200, 500))
        qtbot.mouseMove(schematic.viewport(), target_point, -1)
        qtbot.mouseClick(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.NoModifier,
            target_point,
        )

        assert model_config.edges.get_targets("Link3") == [
            "Link2",
            "Reservoir",
        ]
