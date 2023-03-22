from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig
from pywr_editor.utils import Logging, maybe_delete_component
from pywr_editor.widgets import PushButton

from .table_form_widget import TableFormWidget

if TYPE_CHECKING:
    from .table_pages_widget import TablePagesWidget


class TablePageWidget(QWidget):
    def __init__(
        self, name: str, model_config: ModelConfig, parent: "TablePagesWidget"
    ):
        """
        Initialises the widget with the form to edit a table.
        :param name: The table name.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)

        super().__init__(parent)
        self.name = name
        self.pages = parent
        self.model_config = model_config
        self.table_dict = model_config.tables.get_table_config_from_name(name)
        self.logger.debug(f"Initialising page for table named '{name}'")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # form title
        self.title = FormTitle()
        self.set_page_title(name)

        # button
        # buttons
        close_button = PushButton("Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(parent.dialog.reject)

        # noinspection PyTypeChecker
        save_button = PushButton("Save table")
        save_button.setObjectName("save_button")

        add_button = PushButton("Add new table")
        add_button.setObjectName("add_button")
        # noinspection PyUnresolvedReferences
        add_button.clicked.connect(parent.on_add_new_table)

        delete_button = PushButton("Delete table")
        # noinspection PyUnresolvedReferences
        delete_button.clicked.connect(self.on_delete_table)

        button_box = QHBoxLayout()
        button_box.addWidget(save_button)
        button_box.addWidget(delete_button)
        button_box.addStretch()
        button_box.addWidget(add_button)
        button_box.addWidget(close_button)

        # form
        self.form = TableFormWidget(
            name=name,
            model_config=model_config,
            table_dict=self.table_dict,
            save_button=save_button,
            parent=self,
        )
        # noinspection PyUnresolvedReferences
        save_button.clicked.connect(self.form.on_save)

        layout.addWidget(self.title)
        layout.addWidget(self.form)
        layout.addLayout(button_box)

    def set_page_title(self, table_name: str) -> None:
        """
        Sets the page title.
        :param table_name: The table name.
        :return: None
        """
        self.title.setText(f"Table: {table_name}")

    @Slot()
    def on_delete_table(self) -> None:
        """
        Deletes the selected table.
        :return: None
        """
        dialog = self.pages.dialog
        list_widget = dialog.table_list_widget.list
        list_model = list_widget.model
        # check if table is being used and warn before deleting
        total_components = self.model_config.tables.is_used(self.name)

        # ask before deleting
        if maybe_delete_component(self.name, total_components, self):
            # remove the table from the table model
            # noinspection PyUnresolvedReferences
            list_model.layoutAboutToBeChanged.emit()
            list_model.table_names.remove(self.name)
            # noinspection PyUnresolvedReferences
            list_model.layoutChanged.emit()
            list_widget.clear_selection()

            # remove the page widget
            page_widget = dialog.pages_widget.pages[self.name]
            page_widget.deleteLater()
            del dialog.pages_widget.pages[self.name]

            # delete the table from the model configuration
            self.model_config.tables.delete(self.name)

            # update tree and status bar
            if dialog.app is not None:
                if hasattr(dialog.app, "components_tree"):
                    dialog.app.components_tree.reload()
                if hasattr(dialog.app, "statusBar"):
                    dialog.app.statusBar().showMessage(
                        f'Deleted table "{self.name}"'
                    )

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        """
        Loads the form only when the page is requested.
        :param event: The event being triggered.
        :return: None
        """
        if self.form.loaded is False:
            self.logger.debug(f"Loading fields for table named '{self.name}'")
            self.form.load_fields()

        super().showEvent(event)
