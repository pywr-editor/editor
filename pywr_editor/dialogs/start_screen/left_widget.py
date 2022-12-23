from PySide6.QtWidgets import QDialog, QLabel, QSizePolicy, QVBoxLayout, QWidget

from pywr_editor.style import Color, stylesheet_dict_to_str

from .recent_files_list_widget import RecentFileListWidget


class StartScreenLeftWidget(QWidget):
    def __init__(self, parent: QDialog):
        """
        Initialises the left widget of the dialog.
        :param parent: The parent
        """
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(WindowTitle(self))
        layout.addWidget(WindowSubTitle(self))
        layout.addSpacing(10)
        layout.addWidget(RecentFileListWidget(self))

        self.setStyleSheet(self.stylesheet)
        self.setLayout(layout)
        self.dialog = self.parent()

    @property
    def stylesheet(self) -> str:
        """
        Defines the widget stylesheet.
        :return: The stylesheet as string.
        """
        style = {
            "StartScreenLeftWidget": {
                "background-color": Color("gray", 100).hex,
                "border-left": f'1px solid {Color("gray", 400).hex}',
            }
        }

        return stylesheet_dict_to_str(style)


class WindowTitle(QLabel):
    def __init__(self, parent: QWidget = None):
        """
        Initialises the dialog title.
        :param parent: The parent
        """
        super().__init__(parent)

        self.setText("Pywr editor")
        self.setMaximumHeight(25)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setStyleSheet(
            stylesheet_dict_to_str(
                {
                    "QLabel": {
                        "color": Color("sky", 600).hex,
                        "font-size": "20px",
                    }
                }
            )
        )


class WindowSubTitle(QLabel):
    def __init__(self, parent: QWidget = None):
        """
        Initialises the dialog subtitle.
        :param parent: The parent
        """
        super().__init__(parent)

        self.setText("Recent projects")
        self.setMaximumHeight(25)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setStyleSheet(
            stylesheet_dict_to_str(
                {
                    "QLabel": {
                        "color": Color("gray", 600).hex,
                        "font-size": "15px",
                    }
                }
            )
        )
