from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout

from pywr_editor.form import FormCustomWidget, FormField
from pywr_editor.utils import Logging


class CommentWidget(FormCustomWidget):
    def __init__(self, name: str, value: str, parent: FormField):
        """
        Initialises the comment field with a QPlainTextEdit widget.
        :param name: The field name.
        :param value: The value set for the column.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")

        super().__init__(name, value, parent)

        self.field = QPlainTextEdit()
        self.field.setMaximumHeight(50)
        if value:
            self.field.insertPlainText(value)

        layout = QVBoxLayout()
        layout.addWidget(self.field)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def get_value(self) -> str:
        """
        Returns the comment.
        :return: The comment
        """
        return self.field.toPlainText()
