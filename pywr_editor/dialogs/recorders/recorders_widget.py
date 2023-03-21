from typing import TYPE_CHECKING

from PySide6.QtCore import QSortFilterProxyModel, Qt, QUuid, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from pywr_editor.model import ModelConfig
from pywr_editor.widgets import PushIconButton

from .recorder_pages_widget import RecorderPagesWidget
from .recorders_list_model import RecordersListModel
from .recorders_list_widget import RecordersListWidget

if TYPE_CHECKING:
    from .recorders_dialog import RecordersDialog


class RecordersWidget(QWidget):
    def __init__(self, model_config: ModelConfig, parent: "RecordersDialog"):
        """
        Initialises the widget showing the list of available recorders.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.model_config = model_config
        self.dialog = parent
        self.app = self.dialog.app

        # Model
        self.model = RecordersListModel(
            recorder_names=list(self.model_config.recorders.names),
            model_config=model_config,
        )
        self.add_button = PushIconButton(
            icon=":misc/plus", label="Add", parent=self
        )
        self.delete_button = PushIconButton(
            icon=":misc/minus", label="Delete", parent=self
        )

        # Recorders list
        # sort components by name
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setSortCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        self.list = RecordersListWidget(
            model=self.model,
            proxy_model=self.proxy_model,
            delete_button=self.delete_button,
            parent=self,
        )
        self.list.setModel(self.proxy_model)
        self.list.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addItem(
            QSpacerItem(10, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)

        # noinspection PyUnresolvedReferences
        self.add_button.clicked.connect(self.on_add_new_recorder)
        # noinspection PyUnresolvedReferences
        self.delete_button.clicked.connect(self.on_delete_recorder)

        # Global layout
        layout = QVBoxLayout()
        layout.addWidget(self.list)
        layout.addLayout(button_layout)

        # Style
        self.setLayout(layout)
        self.setMaximumWidth(260)

    @Slot()
    def on_delete_recorder(self) -> None:
        """
        Deletes the selected recorder.
        :return: None
        """
        # check if recorder is being used and warn before deleting
        indexes = self.list.selectedIndexes()
        if len(indexes) == 0:
            return
        recorder_name = self.model.recorder_names[indexes[0].row()]
        total_components = self.model_config.recorders.is_used(recorder_name)

        # ask before deleting
        if self.maybe_delete(recorder_name, total_components, self):
            # remove the recorder from the model
            # noinspection PyUnresolvedReferences
            self.model.layoutAboutToBeChanged.emit()
            self.model.recorder_names.remove(recorder_name)
            # noinspection PyUnresolvedReferences
            self.model.layoutChanged.emit()
            self.list.clear_selection()

            # remove the page widget
            page_widget = self.dialog.pages_widget.pages[recorder_name]
            page_widget.deleteLater()
            del self.dialog.pages_widget.pages[recorder_name]

            # delete the recorder from the model configuration
            self.model_config.recorders.delete(recorder_name)

            # update tree and status bar
            if self.app is not None:
                if hasattr(self.app, "components_tree"):
                    self.app.components_tree.reload()
                if hasattr(self.app, "statusBar"):
                    self.app.statusBar().showMessage(
                        f'Deleted recorder "{recorder_name}"'
                    )

    @Slot()
    def on_add_new_recorder(self) -> None:
        """
        Adds a new recorder. This creates a new scenario in the model and adds, and
        selects the form page.
        :return: None
        """
        # generate unique name
        recorder_name = f"Recorder {QUuid().createUuid().toString()[1:7]}"

        # add the dictionary to the model. Default to NodeRecorder
        # NOTE: the node is not specified and the recorder is not valid
        self.model_config.recorders.update(recorder_name, {"type": "node"})

        # add the page
        pages_widget: RecorderPagesWidget = self.dialog.pages_widget
        pages_widget.add_new_page(recorder_name)
        pages_widget.set_current_widget_by_name(recorder_name)

        # add it to the list model
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.recorder_names.append(recorder_name)
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        # select the item
        new_index = self.proxy_model.mapFromSource(
            self.list.find_index_by_name(recorder_name)
        )
        self.list.setCurrentIndex(new_index)

        # update tree and status bar
        if self.app is not None:
            if hasattr(self.app, "components_tree"):
                self.app.components_tree.reload()
            if hasattr(self.app, "statusBar"):
                self.app.statusBar().showMessage(
                    f'Added new recorder "{recorder_name}"'
                )

    @staticmethod
    def maybe_delete(
        recorder_name: str, total_times: int, parent: QWidget
    ) -> bool:
        """
        Asks user if they want to delete a recorder that's being used by a model
        component.
        :param recorder_name: The recorder name to delete.
        :param total_times: The number of times the recorder is used by the model
        components.
        :param parent: The parent widget.
        :return: True whether to delete the recorder, False otherwise.
        """
        message = f"Do you want to delete {recorder_name}?"
        if total_times > 0:
            times = "time"
            if total_times > 1:
                times = f"{times}s"
            message = (
                f"The recorder '{recorder_name}; you would like to delete is "
                + f"used {total_times} {times} by the model components. If you "
                + "delete it, the model will not be able to run anymore.\n\n"
                + "Do you want to continue?"
            )

        answer = QMessageBox.warning(
            parent,
            "Warning",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            return True
        elif answer == QMessageBox.StandardButton.No:
            return False
        # on discard
        return False
