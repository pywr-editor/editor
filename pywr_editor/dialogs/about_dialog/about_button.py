from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QSizePolicy

from .about_dialog import AboutDialog


class AboutButton(QPushButton):
    def __init__(self):
        """
        Initialises the about button to open the About dialog.
        """
        super().__init__()

        self.setIcon(QIcon(":misc/help"))
        self.setText("")

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setToolTip("Open the About dialog")
        self.setStyleSheet(
            "AboutButton{ background: none; border: 0; padding: 0; }"
        )
        # noinspection PyUnresolvedReferences
        self.clicked.connect(self.show_about_dialog)

    def show_about_dialog(self) -> None:
        """
        Opens the About dialog.
        :return: None
        """
        dialog = AboutDialog(self)
        dialog.show()
