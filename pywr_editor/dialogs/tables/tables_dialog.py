from PySide6.QtWidgets import QMainWindow

from pywr_editor.model import ModelConfig
from pywr_editor.widgets import SettingsDialog

from .table_page_widget import TablePageWidget
from .table_pages_widget import TablePagesWidget
from .tables_widget import TablesWidget


class TablesDialog(SettingsDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        selected_table_name: str = None,
        parent: QMainWindow = None,
    ):
        """
        Initialises the modal dialog.
        :param model_config: The ModelConfig instance.
        :param selected_table_name: The name of the table to select. Default to None.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.app = parent

        # pages - init before list
        self.pages_widget = TablePagesWidget(
            model_config=model_config,
            parent=self,
        )

        # table list
        self.model_config = model_config
        self.table_list_widget = TablesWidget(
            model_config=model_config,
            parent=self,
        )

        self.setup(self.table_list_widget, self.pages_widget)
        self.setWindowTitle("Model tables")
        self.setMinimumSize(850, 700)

        # select a table
        if selected_table_name is not None:
            # load the page and the form fields
            self.pages_widget.set_current_widget_by_name(selected_table_name)
            # noinspection PyTypeChecker
            page: TablePageWidget = self.pages_widget.currentWidget()
            page.form.load_fields()

            table_list = self.table_list_widget.list
            table_list.select_row_by_name(selected_table_name)
