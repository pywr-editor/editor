from PySide6.QtCore import Slot, QUuid
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QMessageBox,
)
from typing import TYPE_CHECKING
from .table_pages_widget import TablePagesWidget
from .tables_list_model import TablesListModel
from .tables_list_widget import TablesListWidget
from pywr_editor.widgets import PushIconButton
from pywr_editor.model import ModelConfig

if TYPE_CHECKING:
    from .tables_dialog import TablesDialog


class TablesWidget(QWidget):
    def __init__(self, model_config: ModelConfig, parent: "TablesDialog"):
        """
        Initialises the widget showing the list of available tables.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.model_config = model_config
        self.dialog = parent
        self.app = self.dialog.app

        # Model
        self.model = TablesListModel(
            table_names=list(self.model_config.tables.names)
        )
        self.add_button = PushIconButton(
            icon=":misc/plus", label="Add", parent=self
        )
        self.delete_button = PushIconButton(
            icon=":misc/minus", label="Delete", parent=self
        )

        # Tables list
        self.list = TablesListWidget(
            model=self.model, delete_button=self.delete_button, parent=self
        )

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addItem(
            QSpacerItem(10, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)

        # noinspection PyUnresolvedReferences
        self.add_button.clicked.connect(self.on_add_new_table)
        # noinspection PyUnresolvedReferences
        self.delete_button.clicked.connect(self.on_delete_table)

        # Global layout
        layout = QVBoxLayout()
        layout.addWidget(self.list)
        layout.addLayout(button_layout)

        # Style
        self.setLayout(layout)
        self.setMaximumWidth(200)

    @Slot()
    def on_delete_table(self) -> None:
        """
        Deletes the selected table.
        :return: None
        """
        # check if table is being used and warn before deleting
        indexes = self.list.selectedIndexes()
        if len(indexes) == 0:
            return
        table_name = self.model.table_names[indexes[0].row()]
        total_components = self.model_config.tables.is_used(table_name)

        # ask before deleting
        if self.maybe_delete(table_name, total_components, self):
            # remove the table from the table model
            # noinspection PyUnresolvedReferences
            self.model.layoutAboutToBeChanged.emit()
            self.model.table_names.remove(table_name)
            # noinspection PyUnresolvedReferences
            self.model.layoutChanged.emit()
            self.list.clear_selection()

            # remove the page widget
            page_widget = self.dialog.pages_widget.pages[table_name]
            page_widget.deleteLater()
            del self.dialog.pages_widget.pages[table_name]

            # delete the table from the model configuration
            self.model_config.tables.delete(table_name)

            # update tree and status bar
            if self.app is not None:
                if hasattr(self.app, "components_tree"):
                    self.app.components_tree.reload()
                if hasattr(self.app, "statusBar"):
                    self.app.statusBar().showMessage(
                        f'Deleted table "{table_name}"'
                    )

    @Slot()
    def on_add_new_table(self) -> None:
        """
        Adds a new table. This creates a new table in the model and adds, and selects
        the form page.
        :return: None
        """
        # generate unique name
        table_name = f"Table {QUuid().createUuid().toString()[1:7]}"

        # add the page
        pages_widget: TablePagesWidget = self.dialog.pages_widget
        pages_widget.add_new_page(table_name)
        pages_widget.set_current_widget_by_name(table_name)

        # add it to the list model
        # noinspection PyUnresolvedReferences
        self.model.layoutAboutToBeChanged.emit()
        self.model.table_names.append(table_name)
        # noinspection PyUnresolvedReferences
        self.model.layoutChanged.emit()
        # select the item (this is always added as last)
        self.list.setCurrentIndex(
            self.model.index(self.model.rowCount() - 1, 0)
        )

        # add the empty dictionary to the model
        self.model_config.tables.update(table_name, {})

        # update tree and status bar
        if self.app is not None:
            if hasattr(self.app, "components_tree"):
                self.app.components_tree.reload()
            if hasattr(self.app, "statusBar"):
                self.app.statusBar().showMessage(
                    f'Added new table "{table_name}"'
                )

    @staticmethod
    def maybe_delete(
        table_name: str, total_times: int, parent: QWidget
    ) -> bool:
        """
        Asks user if they want to delete a table that's being used by a model
        component.
        :param table_name: The table name to delete.
        :param total_times: The number of times the table is used by the model
        components.
        :param parent: The parent widget.
        :return: True whether to delete the table, False otherwise.
        """
        message = f"Do you want to delete {table_name}?"
        if total_times > 0:
            times = "time"
            if total_times > 1:
                times = f"{times}s"
            message = (
                f"The table '{table_name}' you would like to delete is used "
                + f"{total_times} {times} by the model components. If you delete it,"
                + " the model will not be able to run anymore.\n\n"
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
