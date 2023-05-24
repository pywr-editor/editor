from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit, QPlainTextEdit, QVBoxLayout

from pywr_editor.form import FormCustomWidget
from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from pywr_editor.form import FormField


class TextWidget(FormCustomWidget):
    def __init__(
        self, name: str, value: str, parent: "FormField", multi_line: bool = False
    ):
        """
        Initialises the text field with a QLineEdit or QPlainTextEdit widget.
        :param name: The field name.
        :param value: The value.
        :param parent: The parent widget.
        :param multi_line: Whether to show a text area rather than a one line text
        field.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")
        self.multi_line = multi_line

        super().__init__(name, value, parent)

        if multi_line:
            self.line_edit = QPlainTextEdit()
            self.line_edit.setMaximumHeight(50)
            if value:
                self.line_edit.insertPlainText(value)
        else:
            self.line_edit = QLineEdit()
            if value is not None:
                self.line_edit.setText(str(value))
            elif self.field.default_value is not None:
                self.line_edit.setText(str(self.field.default_value))
        self.field_value_changed: Signal = self.line_edit.textChanged

        layout = QVBoxLayout()
        layout.addWidget(self.line_edit)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def get_value(self) -> str:
        """
        Returns the comment.
        :return: The comment
        """
        self.line_edit: QPlainTextEdit | QLineEdit
        return (
            self.line_edit.toPlainText() if self.multi_line else self.line_edit.text()
        )
