from typing import TYPE_CHECKING

from PySide6.QtCore import QUuid, Slot
from PySide6.QtWidgets import QStackedWidget

from pywr_editor.model import ModelConfig

from .table_empty_page_widget import TableEmptyPageWidget
from .table_page_widget import TablePageWidget

if TYPE_CHECKING:
    from pywr_editor.dialogs import TablesDialog


class TablePagesWidget(QStackedWidget):
    def __init__(self, model_config: ModelConfig, parent: "TablesDialog"):
        """
        Initialises the widget showing the list of available tables.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.model_config = model_config
        self.dialog = parent

        self.empty_page = TableEmptyPageWidget(self)
        self.addWidget(self.empty_page)

        self.pages = {}
        for name in model_config.tables.get_all().keys():
            self.add_new_page(name)

        self.set_empty_page()

    def add_new_page(self, table_name: str) -> None:
        """
        Adds a new page.
        :param table_name: The page or table name.
        :return: None
        """
        self.pages[table_name] = TablePageWidget(
            name=table_name, model_config=self.model_config, parent=self
        )
        self.addWidget(self.pages[table_name])

    def rename_page(self, table_name: str, new_table_name: str) -> None:
        """
        Renames a page in the page dictionary.
        :param table_name: The table name to change.
        :param new_table_name: The new table name.
        :return: None
        """
        self.pages[new_table_name] = self.pages.pop(table_name)

    def set_empty_page(self) -> None:
        """
        Sets the empty page as visible.
        :return: None
        """
        self.setCurrentWidget(self.empty_page)

    def set_current_widget_by_name(self, table_name: str) -> None:
        """
        Sets the current widget by providing the table name.
        :param table_name: The table name.
        :return: None
        """
        if table_name in self.pages.keys():
            self.setCurrentWidget(self.pages[table_name])

    @Slot()
    def on_add_new_table(self) -> None:
        """
        Adds a new table. This creates a new table in the model and adds, and selects
        the form page.
        :return: None
        """
        list_widget = self.dialog.table_list_widget.list
        list_model = self.dialog.table_list_widget.model
        proxy_model = self.dialog.table_list_widget.proxy_model

        # generate unique name
        table_name = f"Table {QUuid().createUuid().toString()[1:7]}"

        # add the page
        pages_widget: TablePagesWidget = self.dialog.pages_widget
        pages_widget.add_new_page(table_name)
        pages_widget.set_current_widget_by_name(table_name)

        # add it to the list model
        # noinspection PyUnresolvedReferences
        list_model.layoutAboutToBeChanged.emit()
        list_model.table_names.append(table_name)
        # noinspection PyUnresolvedReferences
        list_model.layoutChanged.emit()

        # select the item
        new_index = proxy_model.mapFromSource(
            list_widget.find_index_by_name(table_name)
        )
        list_widget.setCurrentIndex(new_index)

        # add the empty dictionary to the model
        self.model_config.tables.update(table_name, {})

        # update tree and status bar
        if self.dialog.app is not None:
            if hasattr(self.dialog.app, "components_tree"):
                self.dialog.app.components_tree.reload()
            if hasattr(self.dialog.app, "statusBar"):
                self.dialog.app.statusBar().showMessage(
                    f'Added new table "{table_name}"'
                )
