import os.path
import sys
import traceback
from pathlib import Path
from typing import Literal

import PySide6
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QAction, QKeySequence, Qt, QUndoStack
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QSplitter

from pywr_editor.dialogs import (
    AboutButton,
    EdgeSlotsDialog,
    IncludesDialog,
    JsonCodeViewer,
    MetadataDialog,
    ParametersDialog,
    RecordersDialog,
    ScenariosDialog,
    SearchDialog,
    StartScreen,
    TablesDialog,
)
from pywr_editor.model import ModelConfig
from pywr_editor.schematic import Schematic, scaling_factor
from pywr_editor.style import AppStylesheet
from pywr_editor.toolbar import SchematicItemsLibrary, ToolbarWidget
from pywr_editor.tree import ComponentsTree
from pywr_editor.utils import (
    Action,
    Actions,
    JumpList,
    Logging,
    Settings,
    get_signal_sender,
)


class MainWindow(QMainWindow):
    warning_info_message = Signal(str, str, str)
    """ Signal emitted when a warning message is generated """
    error_message = Signal(str, bool)
    """ Signal emitted when an error message is generated """
    status_message = Signal(str)
    """ Signal emitted when the window status message is updated """
    save = Signal()
    """ Signal emitted when the model is saved """
    store_geometry_widget: list[str] = [
        "toolbar",
        "splitter",
        "components_tree",
        "schematic",
    ]
    """ List of class attributes pointing to widgets whose geometry must be saved """

    def __init__(self, model_file: str | None = None):
        """
        Initialises the editor.
        :param model_file: The path to the model file. Ignore this to start
        a new empty model.
        """
        super().__init__()
        self.logger = Logging().logger(self.__class__.__name__)
        self.warning_info_message.connect(self.on_alert_info_message)
        self.error_message.connect(self.on_error_message)
        self.setStyleSheet(AppStylesheet().get())

        # check the model file
        if model_file is not None and not os.path.exists(model_file):
            QMessageBox().critical(
                self,
                "File not found",
                f"Cannot open the file '{model_file}' because it does not exist.",
            )
            sys.exit(1)
        self.empty_model: bool = False
        if model_file is None:
            self.logger.debug("No model file was provided")
            self.empty_model = True

        # load configurations
        self.model_file = model_file
        self.model_config = ModelConfig(model_file)
        # Show error if the JSON file does not load
        if not self.model_config.is_valid():
            self.error_message.emit(self.model_config.load_error, True)
            return
        self.model_config.changes_tracker.change_applied.connect(
            self.on_model_change
        )

        self.editor_settings = Settings(model_file)
        # store recent files
        if model_file is not None:
            self.editor_settings.save_recent_file(model_file)

        # load widgets
        self.schematic = Schematic(model_config=self.model_config, app=self)
        self.components_tree = ComponentsTree(self.model_config, parent=self)
        self.jump_list = self.setup_jump_list()

        # layout
        self.splitter = QSplitter()
        self.splitter.setOpaqueResize(True)
        self.splitter.setStretchFactor(0, 100)
        self.splitter.addWidget(self.components_tree)
        self.splitter.addWidget(self.schematic)

        # window
        self.set_window_title()
        self.resize(1000, 900)
        self.setAutoFillBackground(True)
        self.setPalette(Qt.GlobalColor.white)
        self.setDockNestingEnabled(False)
        self.setCentralWidget(self.splitter)

        # Actions
        self.undo_stack = QUndoStack(self)
        self.app_actions = Actions(window=self)
        self.register_model_actions()
        self.register_nodes_actions()
        self.register_schematic_actions()
        self.save.connect(self.on_save)

        # Toolbar
        self.toolbar = ToolbarWidget(self)
        self.addToolBar(self.toolbar)
        self.setup_toolbar()

        # Status bar
        self.add_status_bar()
        # noinspection PyUnresolvedReferences
        self.status_message.connect(self.on_status_message)

        # Show the window
        self.editor_settings.restore_window_attributes(self)
        self.show()

        # Draw the widgets
        self.components_tree.draw()
        self.schematic.draw()

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:
        """
        Prompt whether to save the model and saves the widgets' geometry and state.
        :param event: The event being triggered.
        :return: None
        """
        if self.model_config.has_changes is False or self.maybe_save():
            event.accept()
            self.editor_settings.save_window_attributes(self)
        else:
            event.ignore()

    def register_model_actions(self) -> None:
        """
        Registers the action for the model tab.
        :return: None
        """
        self.app_actions.add(
            Action(
                key="new-model",
                name="New\n model",
                icon=":/toolbar/new",
                tooltip="Create a new and empty Pywr model",
                shortcut=QKeySequence.New,
                connection=self.new_empty_model,
            )
        )
        self.app_actions.add(
            Action(
                key="open-model",
                name="Open\n model file",
                icon=":/toolbar/open",
                tooltip="Open a new Pywr model file",
                shortcut=QKeySequence.Open,
                connection=self.open_model_file,
            )
        )
        self.app_actions.add(
            Action(
                key="save-model",
                name="Save\n file",
                icon=":/toolbar/save",
                tooltip="Save the Pywr model file",
                shortcut=QKeySequence.Save,
                connection=self.save_model,
            )
        )
        self.app_actions.add(
            Action(
                key="reload-model",
                name="Reload\n file",
                icon=":/toolbar/reload",
                tooltip="Reload the JSON file if it was externally edited",
                connection=self.reload_model_file,
                button_separator=True,
            )
        )
        self.app_actions.add(
            Action(
                key="search-in-model",
                name="Search",
                icon=":/toolbar/search",
                tooltip="Search the model for parameters, recorders, nodes and tables",
                shortcut=QKeySequence.StandardKey.Find,
                connection=self.search_in_model,
            )
        )
        self.app_actions.add(
            Action(
                key="open-json-reader",
                name="Show\n JSON",
                icon=":/toolbar/show-json",
                tooltip="Show the JSON document in the viewer",
                shortcut=QKeySequence("Ctrl+J"),
                connection=self.show_json,
            )
        )

        self.app_actions.add(
            Action(
                key="edit-metadata",
                name="Metadata",
                icon=":/toolbar/edit-metadata",
                tooltip="Change the model metadata",
                shortcut=QKeySequence("Ctrl+M"),
                connection=self.open_metadata_dialog,
            )
        )
        self.app_actions.add(
            Action(
                key="edit-scenarios",
                name="Scenarios",
                icon=":/toolbar/edit-scenarios",
                tooltip="Change the model scenarios",
                connection=self.open_scenarios_dialog,
            )
        )
        self.app_actions.add(
            Action(
                key="edit-imports",
                name="Imports",
                icon=":/toolbar/edit-imports",
                tooltip="Add and delete imports of custom parameters, nodes and "
                "recorders",
                connection=self.open_imports_dialog,
            )
        )
        self.app_actions.add(
            Action(
                key="edit-slots",
                name="Slots",
                icon=":/toolbar/edit-slots",
                tooltip="Change the name of the nodes' slots",
                connection=self.open_edge_slots_dialog,
            )
        )
        self.app_actions.add(
            Action(
                key="edit-tables",
                name="Tables",
                icon=":/toolbar/edit-tables",
                tooltip="Add, modify and delete the model tables",
                shortcut=QKeySequence("Ctrl+T"),
                connection=self.open_tables_dialog,
            )
        )
        self.app_actions.add(
            Action(
                key="edit-parameters",
                name="Parameters",
                icon=":/toolbar/edit-parameters",
                tooltip="Add, modify and delete the model parameters",
                shortcut=QKeySequence("Ctrl+P"),
                connection=self.open_parameters_dialog,
            )
        )
        self.app_actions.add(
            Action(
                key="edit-recorders",
                name="Recorders",
                icon=":/toolbar/edit-recorders",
                tooltip="Add, modify and delete the model recorders",
                shortcut=QKeySequence("Ctrl+R"),
                connection=self.open_recorders_dialog,
            )
        )

        self.app_actions.add(
            Action(
                key="find-orphaned-nodes",
                name="Check network",
                icon=":/toolbar/find-orphaned-nodes",
                tooltip="Check that all nodes are connected",
                connection=self.check_network,
            )
        )
        self.app_actions.add(
            Action(
                key="find-orphaned-parameters",
                name="Find orphaned parameters",
                icon=":/toolbar/find-orphaned-parameters",
                tooltip="Find orphaned parameters. These are parameters which (1) have "
                + "no\nparent components or (2) are not referenced directly by a node",
                connection=self.find_orphaned_parameters,
            )
        )

    def register_nodes_actions(self):
        """
        Registers the action for the node tab.
        :return: None
        """
        self.app_actions.add(
            Action(
                key="select-all",
                name="Select all",
                icon=":/toolbar/select-all",
                tooltip="Select all nodes on the schematic",
                shortcut=QKeySequence.SelectAll,
                connection=self.schematic.select_all_items,
            )
        )
        self.app_actions.add(
            Action(
                key="select-none",
                name="Select none",
                icon=":/toolbar/select-none",
                tooltip="De-select all nodes on the schematic",
                shortcut=QKeySequence.Deselect,
                connection=self.schematic.de_select_all_items,
                is_disabled=True,
            )
        )
        self.app_actions.add_undo(icon=":/toolbar/undo")
        self.app_actions.add_redo(icon=":/toolbar/redo")
        self.app_actions.add(
            Action(
                key="remove-edges",
                name="Disconnect",
                icon=":/toolbar/remove-edge",
                tooltip="Provides a list of edges to delete for a selected node",
                button_dropdown=True,
                is_disabled=True,
            )
        )
        self.app_actions.add(
            Action(
                key="add-edge",
                name="Connect",
                icon=":/toolbar/add-edge",
                tooltip="Connect a selected node to another one on the schematic",
                is_disabled=True,
            )
        )
        self.app_actions.add(
            Action(
                key="delete-node",
                name="Delete",
                icon=":/toolbar/delete-node",
                tooltip="Delete the selected node and its edges from the schematic",
                is_disabled=True,
            )
        )
        self.app_actions.add(
            Action(
                key="edit-node",
                name="Edit",
                icon=":/toolbar/edit-node",
                tooltip="Edit the configuration of the selected node",
                is_disabled=True,
            )
        )
        # hidden action to abort node connection
        connect_node_action = QAction("Abort connect node")
        connect_node_action.setShortcut(QKeySequence.Cancel)
        # noinspection PyUnresolvedReferences
        connect_node_action.triggered.connect(
            self.schematic.on_connect_node_end
        )
        self.addAction(connect_node_action)
        self.app_actions.registry["connect-node-abort"] = connect_node_action

    def register_schematic_actions(self) -> None:
        """
        Registers the action for the schematic tab.
        :return: None
        """
        self.app_actions.add(
            Action(
                key="increase-width",
                name="Increase\nwidth",
                icon=":toolbar/increase-width",
                tooltip="Increase the width of the schematic",
                connection=self.schematic.increase_width,
            )
        )
        self.app_actions.add(
            Action(
                key="decrease-width",
                name="Decrease\nwidth",
                icon=":toolbar/decrease-width",
                tooltip="Decrease the width of the schematic",
                connection=self.schematic.decrease_width,
                button_separator=True,
            )
        )
        self.app_actions.add(
            Action(
                key="increase-height",
                name="Increase\nheight",
                icon=":toolbar/increase-height",
                tooltip="Increase the height of the schematic",
                connection=self.schematic.increase_height,
            )
        )
        self.app_actions.add(
            Action(
                key="decrease-height",
                name="Decrease\nheight",
                icon=":toolbar/decrease-height",
                tooltip="Decrease the height of the schematic",
                connection=self.schematic.decrease_height,
                button_separator=True,
            )
        )
        self.app_actions.add(
            Action(
                key="minimise",
                name="Minimise",
                icon=":toolbar/minimise-schematic-size",
                tooltip="Minimise the size of the schematic to fit all nodes",
                is_disabled=self.empty_model,
                connection=self.schematic.minimise_size,
            )
        )
        self.app_actions.add(
            Action(
                key="lock",
                name="Lock",
                icon=":toolbar/lock-schematic",
                tooltip="Lock the nodes position on the schematic",
                is_checked=self.editor_settings.is_schematic_locked,
                connection=self.schematic.toggle_lock,
            )
        )
        self.app_actions.add(
            Action(
                key="toggle-labels",
                name="Hide labels",
                icon=":toolbar/toggle-schematic-labels",
                tooltip="Hide or show the node labels on the schematic",
                is_checked=self.editor_settings.are_labels_hidden,
                connection=self.schematic.toggle_labels,
            )
        )
        self.app_actions.add(
            Action(
                key="toggle-arrows",
                name="Hide arrows",
                icon=":toolbar/toggle-schematic-arrows",
                tooltip="Hide or show the edge arrows on the schematic",
                is_checked=self.editor_settings.are_edge_arrows_hidden,
                connection=self.schematic.toggle_arrows,
            )
        )
        self.app_actions.add(
            Action(
                key="center",
                name="Centre",
                icon=":toolbar/centre-schematic",
                tooltip="Centre the schematic",
                connection=self.schematic.center_view_on,
            )
        )
        self.app_actions.add(
            Action(
                key="zoom-in",
                name="Zoom\nin",
                icon=":toolbar/zoom-in",
                tooltip="Zoom in on the schematic",
                shortcut=QKeySequence.ZoomIn,
                connection=self.zoom_in,
            )
        )
        self.app_actions.add(
            Action(
                key="zoom-out",
                name="Zoom\nout",
                icon=":toolbar/zoom-out",
                tooltip="Zoom out on the schematic",
                shortcut=QKeySequence.ZoomOut,
                connection=self.zoom_out,
            )
        )
        self.app_actions.add(
            Action(
                key="zoom-100",
                name="100%",
                icon=":toolbar/zoom-100",
                tooltip="Zoom to 100%",
                is_disabled=True,  # disable when app starts and zoom is at 100%
                connection=self.zoom_100,
            )
        )
        self.app_actions.add(
            Action(
                key="export-current-view",
                name="Export view",
                icon=":toolbar/export-schematic-as-image",
                tooltip="Export current view as image",
                shortcut=QKeySequence("Ctrl+E"),
                connection=self.schematic.export_current_view,
            )
        )

        # register shortcut to delete schematic items
        delete_item_action = QAction("Delete schematic item")
        delete_item_action.setShortcut(QKeySequence.StandardKey.Delete)
        # noinspection PyUnresolvedReferences
        delete_item_action.triggered.connect(
            lambda: self.schematic.on_delete_item(
                self.schematic.scene.selectedItems()
            )
        )
        self.schematic.addAction(delete_item_action)
        self.app_actions.registry["delete-schematic-item"] = delete_item_action

    def setup_toolbar(self) -> None:
        """
        Setups the toolbar.
        :return: None
        """
        # Model tab
        model_tab = self.toolbar.add_tab("Model")
        file_panel = model_tab.add_panel("File")
        file_panel.add_button(self.app_actions.get("new-model"))
        file_panel.add_button(self.app_actions.get("open-model"))
        file_panel.add_button(self.app_actions.get("save-model"))
        self.app_actions.get("save-model").setDisabled(True)
        file_panel.add_button(self.app_actions.get("reload-model"))
        file_panel.add_button(self.app_actions.get("search-in-model"))
        file_panel.add_button(self.app_actions.get("open-json-reader"))

        settings_panel = model_tab.add_panel("Settings")
        settings_panel.add_button(self.app_actions.get("edit-metadata"))
        settings_panel.add_vertical_small_buttons(
            [
                self.app_actions.get("edit-scenarios"),
                self.app_actions.get("edit-imports"),
                self.app_actions.get("edit-slots"),
            ]
        )
        settings_panel.add_button(self.app_actions.get("edit-tables"))
        settings_panel.add_button(self.app_actions.get("edit-parameters"))
        settings_panel.add_button(self.app_actions.get("edit-recorders"))

        validation_panel = model_tab.add_panel("Validation", layout="vertical")
        validation_panel.add_button(
            self.app_actions.get("find-orphaned-nodes"), is_large=False
        )
        validation_panel.add_button(
            self.app_actions.get("find-orphaned-parameters"), is_large=False
        )

        # Schematic tab
        operation_tab = self.toolbar.add_tab("Operations")
        nodes_panel = operation_tab.add_panel("Undo", layout="vertical")
        nodes_panel.add_button(self.app_actions.get("undo"), is_large=False)
        nodes_panel.add_button(self.app_actions.get("redo"), is_large=False)

        nodes_panel = operation_tab.add_panel("Selection", layout="vertical")
        nodes_panel.add_button(
            self.app_actions.get("select-all"), is_large=False
        )
        nodes_panel.add_button(
            self.app_actions.get("select-none"), is_large=False
        )

        op_panel = operation_tab.add_panel("Operations")
        op_panel.add_button(self.app_actions.get("add-edge"))
        op_panel.add_button(self.app_actions.get("remove-edges"))
        op_panel.add_button(self.app_actions.get("edit-node"))
        op_panel.add_button(self.app_actions.get("delete-node"))

        nodes_panel = operation_tab.add_panel("Nodes Library", show_name=False)
        nodes_panel.add_widget(SchematicItemsLibrary(self))

        # View tab
        schematic_tab = self.toolbar.add_tab("Schematic")
        zoom_panel = schematic_tab.add_panel("Zoom")
        zoom_panel.add_button(self.app_actions.get("zoom-in"))
        zoom_panel.add_button(self.app_actions.get("zoom-out"))
        zoom_panel.add_button(self.app_actions.get("zoom-100"))

        display_panel = schematic_tab.add_panel("Display", layout="vertical")
        display_panel.add_button(
            self.app_actions.get("toggle-labels"), is_large=False
        )
        display_panel.add_button(
            self.app_actions.get("toggle-arrows"), is_large=False
        )
        display_panel.add_button(self.app_actions.get("center"), is_large=False)

        size_panel = schematic_tab.add_panel("Size")
        size_panel.add_button(self.app_actions.get("increase-width"))
        size_panel.add_button(self.app_actions.get("decrease-width"))
        size_panel.add_button(self.app_actions.get("increase-height"))
        size_panel.add_button(self.app_actions.get("decrease-height"))
        size_panel.add_button(self.app_actions.get("minimise"), is_large=False)

        misc_panel = schematic_tab.add_panel("Misc", layout="vertical")
        misc_panel.add_button(self.app_actions.get("lock"), is_large=False)
        misc_panel.add_button(
            self.app_actions.get("export-current-view"), is_large=False
        )

    def add_status_bar(self) -> None:
        """
        Adds the status bar
        :return: None
        """
        if self.model_config.load_error is None:
            self.statusBar().showMessage(
                f"Loaded {self.model_config.file.file_name} with "
                + f"{self.model_config.nodes.count} nodes and "
                + f"{self.model_config.edges.count} edges"
            )
        self.statusBar().addPermanentWidget(AboutButton())

    def setup_jump_list(self) -> JumpList:
        """
        Setups the jump list to access recent files
        :return: The JumpList instance.
        """
        jump_list = None

        # noinspection PyBroadException
        try:
            jump_list = JumpList()
            # add recent files
            for file_info in self.editor_settings.get_recent_files():
                jump_list.add_recent_file(
                    title=file_info["title"],
                    file=Path(file_info["file"]),
                )

            # add tasks
            system_icons = (
                Path(os.environ["SystemRoot"]) / "System32" / "shell32.dll"
            )
            jump_list.add_task(
                title="Create new model",
                app_argument=["--create_new"],
                icon=system_icons,
                icon_index=0,
            )
            jump_list.add_task(
                title="Open model file",
                app_argument=["--browse"],
                icon=system_icons,
                icon_index=3,
            )
            jump_list.update()
        except Exception:
            self.logger.debug(
                f"Failed to init JumpList because: {traceback.format_exc()}"
            )

        return jump_list

    def set_window_title(self) -> None:
        """
        Sets the window title.
        :return: None
        """
        if self.model_config.json_file:
            title = f"{self.model_config.title} - {self.model_config.file.name}"
        else:
            title = "New empty model"
        self.setWindowTitle(title)

    def set_zoom(self, scene_scale_factor: float) -> None:
        """
        Zooms in or out on the schematic when the button is clicked.
        :param scene_scale_factor: The factor to use to scale the scene.
        :return: None
        """
        self.schematic.scale_view(scene_scale_factor)

    def zoom_in(self) -> None:
        """
        Zooms in on the schematic.
        :return: None
        """
        self.set_zoom(scaling_factor("zoom-in"))

    def zoom_out(self) -> None:
        """
        Zooms out on the schematic.
        :return: None
        """
        self.set_zoom(scaling_factor("zoom-out"))

    def zoom_100(self) -> None:
        """
        Sets the zoom at 100%.
         :return: None
        """
        self.schematic.reset_scale()

    def maybe_save(self) -> bool:
        """
        Asks user if they want to save the model file before exiting the editor.
        :return: True whether the close the window, False otherwise.
        """
        message = QMessageBox(self)
        message.setWindowTitle("Unsaved changes")
        message.setIcon(QMessageBox.Icon.Information)
        message.setText("The model has been modified")
        message.setInformativeText("Do you want to save your changes?")
        message.setStandardButtons(
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel
        )
        message.setDefaultButton(QMessageBox.StandardButton.Cancel)

        answer = message.exec()
        if answer == QMessageBox.StandardButton.Save:
            return self.save_model()
        elif answer == QMessageBox.StandardButton.Cancel:
            return False
        # on discard close the window
        return True

    def save_model(self) -> bool:
        """
        Saves the model file.
        :return: True if the model was saved. False otherwise
        """
        if self.model_file is not None:
            status = self.model_config.save()
            if status is not True:
                self.error_message.emit(status, False)
            else:
                self.save.emit()
                self.undo_stack.setClean()
        else:
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("JSON file (*.json)")
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.exec()
            files = file_dialog.selectedFiles()
            if len(files) > 0:
                model_file = files[0]
                self.model_file = model_file
                self.model_config.json_file = model_file
                self.save_model()
                self.undo_stack.setClean()
            else:
                return False

        return True

    @Slot()
    def search_in_model(self) -> None:
        """
        Opens the search bar.
        :return: None
        """
        viewer = SearchDialog(parent=self, model_config=self.model_config)
        viewer.exec()

    @Slot()
    def show_json(self) -> None:
        """
        Opens the JSON viewer.
        :return: None
        """
        viewer = JsonCodeViewer(
            parent=self, file_content=self.model_config.json
        )
        viewer.setWindowTitle(self.model_config.file.file_name)
        viewer.exec()

    @Slot()
    def open_metadata_dialog(self) -> None:
        """
        Opens the dialog to edit the model metadata.
        :return: None
        """
        dialog = MetadataDialog(model_config=self.model_config, parent=self)
        dialog.show()

    @Slot()
    def open_imports_dialog(self) -> None:
        """
        Opens the dialog to edit the model imports.
        :return: None
        """
        dialog = IncludesDialog(model_config=self.model_config, parent=self)
        dialog.show()

    @Slot()
    def open_tables_dialog(self) -> None:
        """
        Opens the dialog to edit the model tables.
        :return: None
        """
        dialog = TablesDialog(model_config=self.model_config, parent=self)
        dialog.show()

    @Slot()
    def open_edge_slots_dialog(self) -> None:
        """
        Opens the dialog to edit the model tables.
        :return: None
        """
        dialog = EdgeSlotsDialog(model_config=self.model_config, parent=self)
        dialog.show()

    @Slot()
    def open_parameters_dialog(self) -> None:
        """
        Opens the dialog to edit the model parameters.
        :return: None
        """
        dialog = ParametersDialog(model_config=self.model_config, parent=self)
        dialog.show()

    @Slot()
    def open_recorders_dialog(self) -> None:
        """
        Opens the dialog to edit the model recorders.
        :return: None
        """
        dialog = RecordersDialog(model_config=self.model_config, parent=self)
        dialog.show()

    @Slot()
    def open_scenarios_dialog(self) -> None:
        """
        Opens the dialog to edit the model scenarios.
        :return: None
        """
        dialog = ScenariosDialog(model_config=self.model_config, parent=self)
        dialog.show()

    @Slot(str)
    def on_status_message(self, message: str) -> None:
        """
        Updates the status bar message.
        :param message: The message to write in the status bar.
        :return: None
        """
        self.statusBar().showMessage(message)

    @Slot(str, str, str)
    def on_alert_info_message(
        self, title: str, message: str, alert_type: Literal["warn", "info"]
    ) -> None:
        """
        Shows an alert or info message.
        :param title: The window title.
        :param message: The alert message.
        :param alert_type: The message type (warn or info).
        :return: None
        """
        method = "information"
        if alert_type == "warn":
            method = "warning"
        dialog = getattr(QMessageBox(), method)
        dialog(self, title, message)

    @Slot(str, bool)
    def on_error_message(self, message: str, close: bool) -> None:
        """
        Shows an error message. This closes the application.
        :param message: The error message.
        :param close: Whether to close the application.
        :return: None
        """
        QMessageBox().critical(self, "An error occurred", message)
        if close:
            sys.exit(1)

    @Slot()
    def on_model_change(self) -> None:
        """
        Slot called by the global timer. This listens for model changes.
        :return: None
        """
        self.logger.debug(
            f"Running on_model_change Slot from {get_signal_sender(self)}"
        )
        # enable the "Save" button if there are changes
        save_button = self.app_actions.get("save-model")
        save_button.setEnabled(self.model_config.has_changes)

    @Slot()
    def on_save(self) -> None:
        """
        Performs actions on model save.
        :return: None
        """
        self.logger.debug(
            f"Running on_save Slot from {get_signal_sender(self)}"
        )
        self.statusBar().showMessage(
            f"Model last saved on {self.model_config.file.last_modified_on}"
        )
        self.components_tree.reload()
        self.app_actions.get("save-model").setDisabled(True)
        self.model_config.changes_tracker.reset_change_flag()

    def find_orphaned_parameters(self) -> None:
        """
        Shows a list of orphaned parameters.
        :return: None
        """
        parameter_names = self.model_config.parameters.find_orphans()
        if parameter_names is None:
            status = "info"
            message = "The model does not have any orphaned parameters"
        else:
            status = "warn"
            message = (
                f"The model has {len(parameter_names)} orphaned "
                + f"parameter(s): {', '.join(parameter_names)}"
            )

        # noinspection PyUnresolvedReferences
        self.warning_info_message.emit("Orphaned parameters", message, status)

    def check_network(self) -> None:
        """
        Shows the validation check error if the model does not pass the validation.
        :return: None
        """
        orphaned_nodes = self.model_config.nodes.find_orphans()
        if orphaned_nodes is None:
            status = "info"
            message = "All nodes are properly connected"
        else:
            status = "warn"
            for node_name in orphaned_nodes:
                self.schematic.select_node_by_name(node_name)
            if len(orphaned_nodes) == 1:
                message = (
                    f'The node "{orphaned_nodes[0]}" is not part of a valid route. '
                    + "This has been highlighted on the schematic"
                )
            else:
                message = (
                    f"The following {len(orphaned_nodes)} nodes are not part "
                    + f"of a valid route: {', '.join(orphaned_nodes)}. These "
                    + "have been highlighted on the schematic"
                )

        # noinspection PyUnresolvedReferences
        self.warning_info_message.emit(
            "Model network validation", message, status
        )

    @staticmethod
    @Slot()
    def new_empty_model() -> None:
        """
        Opens a new editor instance to start a new empty model.
        :return: None
        """
        MainWindow()

    @staticmethod
    @Slot()
    def open_model_file() -> None:
        """
        Browse for a new file and load it in the editor.
        :return: None
        """
        dialog = StartScreen()
        dialog.show()

    @Slot()
    def reload_model_file(self) -> None:
        """
        Reloads the JSON file.
        :return: None
        """
        message = QMessageBox(self)
        message.setWindowTitle("Reload model")
        message.setIcon(QMessageBox.Icon.Information)
        message.setText(
            "Do you really want to reload the model? Any unsaved changes will be lost"
        )
        # message.setInformativeText("Do you want to save your changes?")
        message.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        message.setDefaultButton(QMessageBox.StandardButton.Cancel)

        answer = message.exec()
        if answer == QMessageBox.StandardButton.Ok:
            MainWindow(self.model_file)
            self.close()
