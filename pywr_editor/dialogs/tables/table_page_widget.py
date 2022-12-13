import PySide6
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QDialogButtonBox,
    QPushButton,
)
from typing import TYPE_CHECKING
from .table_form_widget import TableFormWidget
from pywr_editor.form import FormTitle
from pywr_editor.utils import Logging
from pywr_editor.model import ModelConfig

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
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save)
        # noinspection PyTypeChecker
        save_button: QPushButton = button_box.findChild(QPushButton)
        save_button.setObjectName("save_button")
        save_button.setText("Update table")

        # form
        self.form = TableFormWidget(
            name=name,
            model_config=model_config,
            table_dict=self.table_dict,
            save_button=save_button,
            parent=self,
        )
        # noinspection PyUnresolvedReferences
        button_box.accepted.connect(self.form.on_save)

        layout.addWidget(self.title)
        layout.addWidget(self.form)
        layout.addWidget(button_box)

    def set_page_title(self, table_name: str) -> None:
        """
        Sets the page title.
        :param table_name: The table name.
        :return: None
        """
        self.title.setText(f"Table: {table_name}")

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
