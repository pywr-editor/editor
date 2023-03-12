from pathlib import Path

import PySide6
from PySide6.QtCore import Slot
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)

from pywr_editor.form import FormTitle
from pywr_editor.model import JsonUtils, ModelConfig
from pywr_editor.utils import Logging, get_signal_sender
from pywr_editor.widgets import PushIconButton, TableView

from .files_model import FilesModel


class IncludesDialog(QDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        parent: QWidget | None = None,
    ):
        """
        Initialises the modal dialog to handle included files.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget. Default to None.
        """
        self.app = parent
        self.model_config = model_config
        self.logger = Logging().logger(self.__class__.__name__)

        super().__init__(parent)

        # title
        title = FormTitle("Custom imports")
        description = QLabel(
            "Add Python files containing custom parameters, nodes and recorders. "
            "Custom classes will be automatically loaded, when you load the model "
            "JSON file with Pywr. The editor will also be able to recognise custom "
            "model components."
        )
        description.setWordWrap(True)

        # Table buttons
        self.add_button = PushIconButton(
            icon=":misc/plus", label="Add file", small=True
        )
        self.add_button.setToolTip("Add a new file to import in the model")
        # noinspection PyUnresolvedReferences
        self.add_button.clicked.connect(self.on_add_new_file)

        self.delete_button = PushIconButton(
            icon=":misc/minus", label="Delete file(s)", small=True
        )
        self.delete_button.setToolTip("Delete the selected import")
        self.delete_button.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.delete_button.clicked.connect(self.on_delete_file)

        # Table
        self.model = FilesModel(
            files_dict=model_config.includes.get_custom_classes(
                include_non_existing=True
            ),
            model_config=model_config,
        )
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.connect(self.on_value_change)

        self.table = TableView(self.model, self.delete_button)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setColumnWidth(0, 300)
        self.table.setItemDelegate(IncludesDelegate())

        table_buttons_layout = QHBoxLayout()
        table_buttons_layout.addStretch()
        table_buttons_layout.addWidget(self.add_button)
        table_buttons_layout.addWidget(self.delete_button)

        # dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Close
        )
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(self.reject)
        button_box.setStyleSheet("margin-top: 20px")
        # noinspection PyTypeChecker
        self.save_button: QPushButton = button_box.findChild(QPushButton)
        self.save_button.setEnabled(False)
        # noinspection PyUnresolvedReferences
        self.save_button.clicked.connect(self.on_save)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.table)
        layout.addLayout(table_buttons_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setMinimumSize(630, 300)
        self.setWindowModality(Qt.WindowModality.WindowModal)

    @Slot()
    def on_delete_file(self) -> None:
        """
        Deletes selected import(s).
        :return: None
        """
        self.logger.debug(
            f"Running on_delete_file Slot from {get_signal_sender(self)}"
        )
        indexes = self.table.selectedIndexes()
        row_indexes = list({index.row() for index in indexes})
        file_names = list(self.model.files_dict.keys())

        # check that a class in the files h=that are going to be deleted is not used
        # in any "type" key
        used_classes = []
        occurrences = 0
        import_attrs = ["parameters", "recorders", "nodes"]
        for ri in row_indexes:
            import_props = self.model.files_dict[file_names[ri]]
            for attr in import_attrs:
                for component_name in getattr(import_props, attr):
                    matches = JsonUtils(self.model_config.json).find_str(
                        string=component_name, match_key="type"
                    )
                    occurrences += matches.occurrences
                    if matches.occurrences:
                        used_classes.append(component_name)

        if used_classes:
            comp_word = "component" if occurrences == 1 else "components"
            message = "The custom import you are going to delete contains the "
            message += f"following Python classes that are used by {occurrences} model "
            message += f"{comp_word}: {', '.join(used_classes)}\n\n"
            message += "Do you want to continue?"

            answer = QMessageBox.warning(
                self,
                "Warning",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.No:
                return

        # delete imports
        new_files = {}
        for fi, file in enumerate(self.model.files_dict):
            if fi in row_indexes:
                self.logger.debug(f"Deleted import '{file}'")
            else:
                new_files[file] = self.model.files_dict[file]

        # update the model
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.files_dict = new_files
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        self.table.clear_selection()

    @Slot()
    def on_add_new_file(self) -> None:
        """
        Adds a new import.
        :return: None
        """
        self.logger.debug(
            f"Running on_add_file Slot from {get_signal_sender(self)}"
        )
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)

        files_filter = "Python (*.py)"
        file_dialog.setNameFilter(files_filter)

        file_dialog.exec()
        files = file_dialog.selectedFiles()
        if len(files) == 0:
            return

        self.add_files(files)

    def add_files(self, files: list[str]) -> None:
        """
        Adds new files to the table.
        :param files: The list of files to add.
        :return: None
        """
        self.logger.debug(f"Selected {files}")
        for file in files:
            file = Path(file)
            file_name = file.name
            self.logger.debug(f"Processing '{file_name}'")
            error_message = None

            # check that file can be imported
            if not file.exists():
                error_message = f"The file '{file_name}' does not exist"
            elif not str(file).endswith(".py"):
                error_message = (
                    f"The file '{file_name}' must be a valid Python (.py) file"
                )
            elif file in self.model.files_dict:
                error_message = (
                    f"The file '{file_name}' is already in the import list"
                )

            # show error
            if error_message:
                self.logger.debug(error_message)
                QMessageBox.critical(
                    self, "Error", error_message, QMessageBox.StandardButton.Ok
                )
                continue

            # parse the file
            # noinspection PyBroadException
            try:
                import_props = self.model_config.includes.get_classes_from_file(
                    file
                )
                if (
                    not import_props.parameters
                    and not import_props.recorders
                    and not import_props.nodes
                ):
                    QMessageBox.warning(
                        self,
                        "Warning",
                        f"The file '{file_name}' does not contain any valid pywr "
                        "classes. The classes must inherit from Parameter (for "
                        "parameters), or Node (for nodes) or Recorder (for recorders)",
                        QMessageBox.StandardButton.Ok,
                    )
                    self.logger.debug("Invalid base class")

                self.logger.debug("File added")
                # update the model
                # noinspection PyUnresolvedReferences
                self.model.layoutAboutToBeChanged.emit()
                self.model.files_dict[file] = import_props
                # noinspection PyUnresolvedReferences
                self.model.layoutChanged.emit()
            except Exception:
                self.logger.debug(
                    f"An error occurred while parsing the Python file '{file_name}'"
                )
                QMessageBox.critical(
                    self,
                    "Error",
                    f"The file '{file.as_posix()}' cannot be parsed. Make sure it"
                    "does not contain syntax errors and includes valid Python "
                    "classes",
                    QMessageBox.StandardButton.Ok,
                )

    @Slot()
    def on_save(self) -> None:
        """
        Saves the import list.
        :return: None
        """
        self.logger.debug(
            f"Running on_add_file Slot from {get_signal_sender(self)}"
        )

        # includes non Python files
        values = self.model_config.includes.get_all_non_pyfiles()
        # convert to relative path
        for file in self.model.files_dict.keys():
            values.append(self.model_config.path_to_relative(file, True))
        self.logger.debug(f"Saving {values}")
        self.model_config.includes.save_imports(values)

        # update the node panel
        if self.app:
            from pywr_editor.toolbar.node_library.schematic_items_library import (
                LibraryPanel,
            )

            # noinspection PyTypeChecker
            panel: LibraryPanel = self.app.findChild(LibraryPanel)
            panel.reload()

        self.save_button.setEnabled(False)

    @Slot()
    def on_value_change(self) -> None:
        """
        Enables the save button when the model changes.
        :return: None
        """
        self.save_button.setEnabled(True)


class IncludesDelegate(QStyledItemDelegate):
    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionViewItem,
        index: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex,
    ):
        """
        Paints the row red when file does not exist.
        :param painter: The painter instance.
        :param option: The option.
        :param index: The item index.
        :return: None
        """
        background = index.data(Qt.ItemDataRole.BackgroundRole)
        if background:
            painter.fillRect(option.rect, background)

        super().paint(painter, option, index)
