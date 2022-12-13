import pytest
from typing import Tuple
from PySide6 import QtCore, QtGui
from PySide6.QtCore import QPoint, QMimeData, QEvent, QObject
from PySide6.QtGui import Qt, QDragEnterEvent
from PySide6.QtWidgets import QWidget
from pywr_editor import MainWindow
from pywr_editor.schematic import Schematic
from pywr_editor.toolbar.tab_panel import TabPanel
from tests.utils import resolve_model_path


class EventFilter(QObject):
    def eventFilter(self, obj: QWidget, event: QEvent):
        super().eventFilter(obj, event)
        return False


class TestAddNodes:
    model_file = resolve_model_path("model_1.json")

    @pytest.fixture
    def init_window(self) -> Tuple[MainWindow, Schematic, TabPanel]:
        """
        Initialises the window.
        :return: A tuple with the window, schematic and tab panel instances.
        """
        window = MainWindow(self.model_file)
        window.hide()
        schematic = window.schematic
        node_lib_panel = window.toolbar.tabs["Nodes"].panels["Nodes Library"]

        return window, schematic, node_lib_panel

    # def test_start_drag_action(self, qtbot, init_window) -> None:
    #     """
    #     Test that the drag action properly starts when a node is dragged from
    #     the node library.
    #     """
    #     window, schematic, nodes_lib_panel = init_window
    #     # noinspection PyTypeChecker
    #     nodes_lib_widget: NodesLibrary = nodes_lib_panel.widgets[0]
    #     viewport = nodes_lib_widget.viewport()
    #
    #     # application must be visible
    #     qtbot.wait(300)
    #     window.show()
    #
    #     filter = EventFilter(window)
    #     # start the drag action
    #     # nodes_lib_widget.installEventFilter(filter)
    #     viewport.installEventFilter(filter)
    #
    #     # qtbot.mousePress does not work on QGraphicsItem
    #     p = QPoint(30, 30)
    #     qtbot.mousePress(nodes_lib_widget, Qt.MouseButton.LeftButton, Qt.NoModifier, p)
    #     mime_data = QMimeData()
    #     mime_data.setText("Link")
    #     event = QDragMoveEvent(
    #         p,
    #         Qt.CopyAction,
    #         mime_data,
    #         Qt.MouseButton.LeftButton,
    #         Qt.NoModifier,
    #     )
    #     QApplication.postEvent(viewport, event)
    #     qtbot.mouseRelease(viewport, Qt.MouseButton.LeftButton, Qt.NoModifier, p)

    def test_drag_node_to_schematic(self, qtbot, init_window) -> None:
        """
        Tests that when a node is dropped onto the schematic, the node is correctly
        added to the model and the schematic. This tests the dragEnterEvent and
        dropEvent methods in the Schematic class.
        """
        window, schematic, _ = init_window
        model_config = schematic.model_config
        item_count = len(schematic.schematic_items)

        # drop a link node
        mime_data = QMimeData()
        mime_data.setText("Link")

        # start the drop event
        scene_pos = QPoint(100, 50)
        # noinspection PyTypeChecker
        event = QDragEnterEvent(
            scene_pos,
            Qt.DropAction.CopyAction,
            mime_data,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        QtCore.QCoreApplication.sendEvent(schematic.viewport(), event)

        # drop the node
        # noinspection PyTypeChecker
        event = QtGui.QDropEvent(
            scene_pos,
            Qt.DropAction.MoveAction,
            mime_data,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            QEvent.Drop,
        )
        QtCore.QCoreApplication.sendEvent(schematic.viewport(), event)

        # check that the new node is in the schematic
        new_item_count = len(schematic.schematic_items)
        new_node_name = list(schematic.schematic_items.keys())[-1]
        assert new_item_count == item_count + 1
        assert "Node " in list(schematic.schematic_items.keys())[-1]

        assert model_config.has_changes is True
        # the node is in the model configuration
        assert (
            model_config.nodes.find_node_index_by_name(new_node_name)
            is not None
        )
        # the node dictionary is correct
        node_dict = model_config.nodes.get_node_config_from_name(new_node_name)
        node_pos = schematic.mapToScene(scene_pos).toTuple()

        assert node_dict["name"] == new_node_name
        assert node_dict["type"] == "Link"
        assert node_dict["position"]["editor_position"][0] == round(
            node_pos[0], 4
        )
        assert node_dict["position"]["editor_position"][1] == round(
            node_pos[1], 4
        )
