from PySide6.QtGui import Qt
from PySide6.QtWidgets import QTableWidget, QWidget

from pywr_editor.style import stylesheet_dict_to_str

from .table_view import TableView


class TableWidget(QTableWidget):
    def __init__(
        self, row_count: int = 0, column_count: int = 0, parent: QWidget = None
    ):
        """
        Initialises the TableWidget.
        :param row_count: The number of rows. Default to 0.
        :param column_count: The number of columns. Default to 0.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(row_count, column_count, parent)

        # style
        self.setSortingEnabled(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.horizontalHeader().setHighlightSections(False)

        self.verticalHeader().hide()
        self.setAlternatingRowColors(False)

        style = TableView.stylesheet(as_string=False)
        for key, value in style.items():
            if "TableView" in key:
                del style[key]
                key = key.replace("TableView", "TableWidget")
                style[key] = value

        self.setStyleSheet(stylesheet_dict_to_str(style))
        self.verticalScrollBar().setContextMenuPolicy(
            Qt.ContextMenuPolicy.NoContextMenu
        )
