from typing import TYPE_CHECKING

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

        self.empty_page = TableEmptyPageWidget()
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
