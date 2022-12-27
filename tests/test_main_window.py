from functools import partial

import pytest
from PySide6.QtCore import QTimer

from pywr_editor import MainWindow
from pywr_editor.toolbar.node_library.library_item import LibraryItem
from pywr_editor.toolbar.node_library.library_item_label import LibraryItemLabel
from pywr_editor.toolbar.node_library.schematic_items_library import (
    LibraryPanel,
)
from tests.utils import check_msg, resolve_model_path


class TestMainWindow:
    def test_file_not_found(self, qtbot):
        """
        Tests that the window shows a warning message if the JSON file does not exists.
        """
        with pytest.raises(SystemExit) as e:
            QTimer.singleShot(
                100,
                partial(
                    check_msg, "Cannot open the file 'non_existing_file.json'"
                ),
            )
            window = MainWindow("non_existing_file.json")
            window.close()
            assert e.type == SystemExit
            assert e.value.code == 1

    def test_load_model(self, qtbot):
        """
        Tests the MainWindow class when a new model loaded.
        """
        window = MainWindow(resolve_model_path("model_1.json"))
        assert window.empty_model is False
        window.close()

    def test_on_model_change(self, qtbot):
        """
        Tests the on_model_change Slot. The "Save" button is enabled when a new
        change is made; the user is prompted to save the model if there are
        unsaved changes.
        """
        window = MainWindow(resolve_model_path("model_1.json"))
        save_button = window.app_actions.get("save-model")
        # button gets disabled after a few ms
        qtbot.wait(600)
        assert save_button.isEnabled() is False

        # make a change - button is enabled after 500 ms in the main loop
        window.model_config.changes_tracker.add("New change")
        qtbot.wait(600)
        assert save_button.isEnabled() is True

        # with changes the prompt is shown
        QTimer.singleShot(
            600,
            partial(check_msg, "The model has been modified"),
        )
        window.close()

    def test_node_library(self, qtbot):
        """
        Check that the shape for the custom nodes are included in the
        node library.
        """
        window = MainWindow(resolve_model_path("model_1.json"))
        window.hide()

        # check that the imported node is in the panel
        panel: LibraryPanel = window.toolbar.findChild(LibraryPanel)
        found_imported = False
        found_generic_custom = False
        for item in panel.items():
            if isinstance(item, LibraryItemLabel):
                if item.text() == "LeakyPipe":
                    found_imported = True
                elif item.text() == LibraryItem.not_import_custom_node_name:
                    found_generic_custom = True
        assert found_imported is True
        assert found_generic_custom is True
