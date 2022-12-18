import pytest
from functools import partial
from PySide6.QtCore import QTimer
from pywr_editor import MainWindow
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
        save_button = window.actions.get("save-model")
        # button gets disabled after a few ms
        qtbot.wait(300)
        assert save_button.isEnabled() is False

        # make a change - button is enabled after 500 ms in the main loop
        window.model_config.changes_tracker.add("New change")
        qtbot.wait(600)
        assert save_button.isEnabled() is True

        # with changes the prompt is shown
        QTimer.singleShot(
            500,
            partial(check_msg, "The model has been modified"),
        )
        window.close()
