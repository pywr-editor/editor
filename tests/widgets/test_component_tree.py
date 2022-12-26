from typing import Tuple

import pytest
from PySide6.QtCore import Qt, QTimer

from pywr_editor import MainWindow
from pywr_editor.tree import ComponentsTree
from tests.utils import close_message_box, resolve_model_path


class TestComponentTree:
    model_file = resolve_model_path("model_1.json")

    @pytest.fixture
    def init_window(self) -> Tuple[MainWindow, ComponentsTree]:
        """
        Initialises the window.
        :return: A tuple with the window and the component's tree instances.
        """
        QTimer.singleShot(100, close_message_box)
        window = MainWindow(resolve_model_path(self.model_file))
        window.hide()
        tree = window.components_tree

        return window, tree

    def test_save_expanded_status(self, qtbot, init_window):
        """
        Checks that, after the model is saved and the component's tree is refreshed,
        the items that were expanded are still in the expanded state.
        """
        window, tree_widget = init_window

        def fetch_items(tree: ComponentsTree):
            return [
                tree.findItems("Nodes", Qt.MatchExactly | Qt.MatchRecursive, 0)[
                    0
                ],
                # Nodes -> Links
                tree.findItems(
                    "Link (", Qt.MatchContains | Qt.MatchRecursive, 0
                )[0],
                # Nodes -> Links -> Link
                tree.findItems("Link", Qt.MatchExactly | Qt.MatchRecursive, 0)[
                    0
                ],
                tree.findItems(
                    "param2", Qt.MatchExactly | Qt.MatchRecursive, 0
                )[0],
            ]

        # expands the item. This calls the appropriate slot
        for item in fetch_items(tree_widget):
            item.setExpanded(True)

        # reload tree and check that all items are still expanded
        tree_widget.reload()
        assert all(item.isExpanded() for item in fetch_items(tree_widget))

        # collapse the Nodes item and reload
        item = fetch_items(tree_widget)[0]
        item.setExpanded(False)
        tree_widget.reload()
        # check that the Node item is collapsed and the others still expanded
        assert fetch_items(tree_widget)[0].isExpanded() is False
        assert all(item.isExpanded() for item in fetch_items(tree_widget)[1:])

    def test_click_on_item(self, qtbot, init_window):
        """
        Checks that the clicked node is highlighted on the schematic.
        """
        window, tree_widget = init_window

        # simulate click by calling the slot
        tree_item = tree_widget.findItems(
            "Reservoir", Qt.MatchExactly | Qt.MatchRecursive, 0
        )[0]
        tree_widget.on_item_click(tree_item)
        # node must be selected
        assert (
            window.schematic.node_items[tree_item.text(0)].isSelected() is True
        )
