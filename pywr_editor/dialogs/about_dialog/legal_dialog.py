import qtawesome as qta
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .about_dialog_style_sheet import about_dialog_stylesheet


class LegalDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        """
        Initialises the dialog.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Legal notices")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(about_dialog_stylesheet())

        width, height = (600, 450)
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)

        # add layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        # Title
        title = QLabel(
            '<div style="font-weight:bold; font-size:16px">Legal notices</div>'
        )
        # Text area
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        fid = open("LEGAL NOTICES.md", "r")
        text_area.setMarkdown(fid.read())
        fid.close()

        # Button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(self.reject)
        # noinspection PyUnresolvedReferences
        button_box.findChild(QPushButton).setIcon(qta.icon("msc.close"))

        layout.addWidget(title)
        layout.addWidget(text_area)
        layout.addWidget(button_box)
