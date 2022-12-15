import PySide6
from PySide6.QtCore import QByteArray, QFile, QTextStream, Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
from typing import TYPE_CHECKING, Callable
from .action_button import StartScreenActionButton
from .recent_files_list_widget import RecentFileListWidget
from pywr_editor.style import Color, stylesheet_dict_to_str

if TYPE_CHECKING:
    from .start_screen import StartScreen


class StartScreenRightWidget(QFrame):
    def __init__(self, parent: "StartScreen"):
        """
        Initialises the left widget of the dialog.
        :param parent: The dialog screen.
        """
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(0)

        layout.addWidget(CloseButton(parent))

        # noinspection PyTypeChecker
        recent_project_widget: RecentFileListWidget = parent.findChild(
            QListWidget
        )
        buttons = [
            {
                "title": "New file",
                "description": "Create a new model",
                "qrc_icon": ":toolbar/new",
                "action": self.new_empty_model,
            },
            {
                "title": "Browse files",
                "description": "Open a new model",
                "qrc_icon": ":toolbar/open",
                "action": recent_project_widget.browse_files,
            },
            {
                "title": "Clear recent projects",
                "description": "Clear the list of recent projects",
                "qrc_icon": ":toolbar/listbox",
                "action": recent_project_widget.clear,
            },
        ]

        for button in buttons:
            layout.addWidget(
                StartScreenActionButton(
                    title=button["title"],
                    description=button["description"],
                    qrc_icon=button["qrc_icon"],
                    action=button["action"],
                    parent=self,
                )
            )

        layout.addItem(
            QSpacerItem(
                10, 10, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding
            )
        )
        self.setLayout(layout)
        self.setStyleSheet(self.stylesheet)

    @property
    def stylesheet(self) -> str:
        """
        Defines the widget stylesheet.
        :return: The stylesheet as string.
        """
        style = {
            "StartScreenRightWidget": {
                "background-color": "white",
                "border": f'1px solid {Color("gray", 300).hex}',
            },
        }

        return stylesheet_dict_to_str(style)

    def new_empty_model(self) -> None:
        """
        Opens the editor to start a new empty model.
        :return: None
        """
        from pywr_editor.main_window import MainWindow

        MainWindow()
        self.parent().close()


class CloseButton(QWidget):
    def __init__(self, parent: "StartScreen"):
        """
        Initialises the close button widget
        :param parent: The dialog window.
        """
        super().__init__(parent)

        button = ButtonContainer(parent, parent.close)

        h_layout = QHBoxLayout()
        h_layout.setSpacing(0)
        self.icon = SvgCloseIcon(self)
        h_layout.addWidget(self.icon)
        button.setLayout(h_layout)

        wrapper_layout = QHBoxLayout()
        wrapper_layout.setSpacing(0)
        wrapper_layout.addWidget(button)
        wrapper_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.setLayout(wrapper_layout)
        self.setStyleSheet(
            "QPushButton { background: transparent; border: 0px; }"
        )


class ButtonContainer(QPushButton):
    def __init__(self, parent: "StartScreen", action: Callable):
        """
        Initialises the close button container.
        :param parent: The dialog window.
        :param action: The action to perform when the button is clicked.
        """
        super().__init__(parent)
        self.opacity = QGraphicsOpacityEffect(self)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setFlat(True)
        self.setMaximumHeight(38)
        self.setMaximumWidth(38)
        # noinspection PyUnresolvedReferences
        self.clicked.connect(action)

    def enterEvent(self, event: PySide6.QtGui.QEnterEvent) -> None:
        """
        Applies the opacity on mouse enter.
        :param event: The event being triggered.
        :return: None
        """
        self.opacity.setOpacity(0.6)
        self.setGraphicsEffect(self.opacity)

    def leaveEvent(self, event: PySide6.QtCore.QEvent) -> None:
        """
        Resets the opacity on mouse leave.
        :param event: The event being triggered.
        :return: None
        """
        self.opacity.setOpacity(1)
        self.setGraphicsEffect(self.opacity)


class SvgCloseIcon(QSvgWidget):
    def __init__(
        self, parent: QWidget = None, icon: str = ":file-browser/close"
    ):
        """
        Initialises the close icon.
        :param parent: The parent
        :param icon: The path to the resource icon.
        """
        super().__init__(parent)

        self.icon = icon
        self.renderer().load(self.svg_bytes)
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding
        )

    @property
    def svg_bytes(self) -> PySide6.QtCore.QByteArray:
        """
        Loads the icon and replace its colour.
        :return: The QByteArray instance.
        """
        f = QFile(self.icon)
        f.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(f)
        svg_data = stream.readAll()
        f.close()

        svg_data = svg_data.replace("currentColor", Color("blue", 500).hex)
        # noinspection PyTypeChecker
        return QByteArray(svg_data)
