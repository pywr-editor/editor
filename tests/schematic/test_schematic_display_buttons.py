from typing import Tuple

import pytest
from PySide6.QtCore import Qt, QTimer

from pywr_editor import MainWindow
from pywr_editor.schematic import Edge, Schematic, SchematicLabel
from pywr_editor.toolbar.tab_panel import TabPanel
from pywr_editor.utils import Settings
from tests.utils import close_message_box, resolve_model_path


class TestSchematicDisplayButtons:
    model_file = resolve_model_path("model_1.json")

    @pytest.fixture
    def init_window(self) -> Tuple[MainWindow, Schematic, TabPanel]:
        """
        Initialises the window.
        :return: A tuple with the window, schematic and tab panel instances.
        """
        QTimer.singleShot(100, close_message_box)
        window = MainWindow(resolve_model_path(self.model_file))
        window.hide()
        schematic = window.schematic
        size_panel = window.toolbar.tabs["Schematic"].panels["Display"]

        return window, schematic, size_panel

    def test_toggle_hide_labels_button(self, qtbot, init_window):
        """
        Tests that, when the hide labels button is clicked, all the labels are hidden
        and that the configuration is stored via QSettings.
        """
        window, schematic, size_panel = init_window
        button = size_panel.buttons[window.app_actions.get("toggle-labels").text()]

        # disable labels
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        # button is checked
        assert button.isChecked() is True
        for item in schematic.items():
            if isinstance(item, SchematicLabel):
                # labels are hidden
                assert item.hide_label is True
        # config is updated
        assert window.editor_settings.are_labels_hidden is True

        # re-enable labels
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert button.isChecked() is False
        for item in schematic.items():
            if isinstance(item, SchematicLabel):
                assert item.hide_label is False
        assert window.editor_settings.are_labels_hidden is False

    @pytest.fixture()
    def hide_labels(self) -> None:
        """
        Hides the schematic labels.
        :return: None
        """
        editor_settings = Settings(self.model_file)
        editor_settings.save_hide_labels(True)
        editor_settings.instance.sync()

    def test_show_labels(self, qtbot, hide_labels, init_window):
        """
        Tests that, when the labels are initially hidden and the hide labels button
        is clicked, all the labels are shown and that the configuration is stored via
        QSettings.
        """
        window, schematic, size_panel = init_window
        button = size_panel.buttons[window.app_actions.get("toggle-labels").text()]
        # labels are initially hidden
        assert window.editor_settings.are_labels_hidden is True

        # enable labels
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        # button must be checked
        assert button.isChecked() is False
        for item in schematic.items():
            if isinstance(item, SchematicLabel):
                # labels must be visible
                assert item.hide_label is False

    def test_toggle_hide_arrows_button(self, qtbot, init_window):
        """
        Tests that, when the hide arrows button is clicked, all the arrows are hidden
        and that the configuration is stored via QSettings.
        """
        window, schematic, size_panel = init_window
        button = size_panel.buttons[window.app_actions.get("toggle-arrows").text()]

        # disable labels
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        # button is checked
        assert button.isChecked() is True
        for item in schematic.items():
            if isinstance(item, Edge):
                # arrows are hidden
                assert item.hide_arrow is True
        # config is updated
        assert window.editor_settings.are_edge_arrows_hidden is True

        # re-enable labels
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert button.isChecked() is False
        for item in schematic.items():
            if isinstance(item, Edge):
                assert item.hide_arrow is False
        assert window.editor_settings.are_edge_arrows_hidden is False

    @pytest.fixture()
    def hide_arrows(self) -> None:
        """
        Hides the schematic arrows.
        :return: None
        """
        editor_settings = Settings(self.model_file)
        editor_settings.save_hide_arrows(True)
        editor_settings.instance.sync()

    def test_show_arrows(self, qtbot, hide_arrows, init_window):
        """
        Tests that, when the arrows are initially hidden and the hide arrows button is
        clicked, all the arrows are shown and that the configuration is stored via
        QSettings.
        """
        window, schematic, size_panel = init_window
        button = size_panel.buttons[window.app_actions.get("toggle-arrows").text()]
        # labels are initially hidden
        assert window.editor_settings.are_edge_arrows_hidden is True

        # enable arrows
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        # button must be checked
        assert button.isChecked() is False
        for item in schematic.items():
            if isinstance(item, Edge):
                # arrows must be visible
                assert item.hide_arrow is False
