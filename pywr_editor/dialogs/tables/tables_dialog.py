from typing import TYPE_CHECKING, Union

from PySide6.QtCore import QSortFilterProxyModel, Qt, QUuid, Slot
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QDialog, QHBoxLayout

from pywr_editor.model import ModelConfig

from ..base.component_dialog_splitter import ComponentDialogSplitter
from ..base.component_list import ComponentList
from ..base.component_pages import ComponentPages
from .table_empty_page import TableEmptyPage
from .table_page import TablePage
from .tables_list_model import TablesListModel

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class TablesDialog(QDialog):
    def __init__(
        self,
        model: ModelConfig,
        selected_name: str = None,
        parent: Union[QWindow, "MainWindow", None] = None,
    ):
        """
        Initialise the modal dialog.
        :param model: The ModelConfig instance.
        :param selected_name: The name of the table to select. Default to None.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.app = parent
        self.model = model

        # Right widget
        self.pages = ComponentPages(self)

        # add pages
        empty_page = TableEmptyPage(self.pages)
        self.pages.add_page("empty_page", empty_page, True)
        for name in model.tables.names:
            self.pages.add_page(name, TablePage(name, model, self.pages))

        # Left widget
        # models
        self.list_model = TablesListModel(
            table_names=list(model.tables.names),
            model_config=model,
        )
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.list_model)
        self.proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        # widget
        self.list = ComponentList(self.list_model, self.proxy_model, empty_page, self)
        self.list.setMaximumWidth(290)

        # setup dialog
        self.setWindowTitle("Tables")
        self.setMinimumSize(1000, 750)

        splitter = ComponentDialogSplitter(self.list, self.pages, self.app)

        modal_layout = QHBoxLayout(self)
        modal_layout.setContentsMargins(0, 0, 5, 0)
        modal_layout.addWidget(splitter)

        # select a table
        if selected_name is not None:
            found = self.pages.set_page_by_name(selected_name)
            if found is False:
                return

            # noinspection PyTypeChecker
            page: TablePage = self.pages.currentWidget()
            page.form.load_fields()
            # set the selected item in the list
            self.list.table.select_row_by_name(selected_name)

    @Slot()
    def add_table(self) -> None:
        """
        Add a new table. This creates a new table in the model and adds, and selects
        the form page.
        :return: None
        """
        # generate unique name
        table_name = f"Table {QUuid().createUuid().toString()[1:7]}"

        # add the page
        new_page = TablePage(table_name, self.model, self.pages)
        self.pages.add_page(table_name, new_page)
        self.pages.set_page_by_name(table_name)

        # add it to the list model
        self.list_model.layoutAboutToBeChanged.emit()
        self.list_model.table_names.append(table_name)
        self.list_model.layoutChanged.emit()

        # select the item
        table = self.list.table
        new_index = self.proxy_model.mapFromSource(table.find_index_by_name(table_name))
        table.setCurrentIndex(new_index)

        # add the empty dictionary to the model
        self.model.tables.update(table_name, {})

        # update tree and status bar
        if self.app is not None:
            if hasattr(self.app, "components_tree"):
                self.app.components_tree.reload()
            if hasattr(self.app, "statusBar"):
                self.app.statusBar().showMessage(f'Added new table "{table_name}"')
