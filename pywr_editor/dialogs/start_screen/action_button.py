import PySide6
from typing import Callable
from PySide6.QtCore import QByteArray, QFile, QTextStream
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from pywr_editor.style import Color, stylesheet_dict_to_str


class StartScreenActionButton(QWidget):
    def __init__(
        self,
        title: str,
        description: str,
        qrc_icon: str,
        action: Callable,
        parent,
    ):
        """
        Initialises the button.
        :param title: The button title.
        :param description: The button description.
        :param qrc_icon: The path to the resource icon.
        :param action: The action to perform when the button is clicked.
        :param parent: The parent.
        """
        super().__init__(parent)
        button = QPushButton()
        button.setMaximumHeight(60)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setFlat(True)
        # noinspection PyUnresolvedReferences
        button.clicked.connect(action)

        h_layout = QHBoxLayout()
        h_layout.addWidget(Icon(qrc_icon))

        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)
        v_layout.addWidget(TitleLabel(title))
        v_layout.addWidget(DescriptionLabel(description))

        h_layout.addLayout(v_layout)
        button.setLayout(h_layout)

        wrapper_layout = QGridLayout()
        wrapper_layout.setSpacing(0)
        wrapper_layout.addWidget(button)

        self.setLayout(wrapper_layout)
        self.setStyleSheet(self.stylesheet)

    @property
    def stylesheet(self) -> str:
        """
        Defines the widget stylesheet.
        :return: The stylesheet as string.
        """
        style = {
            "QPushButton": {
                "background": "transparent",
                "border": "0px",
                "color": Color("gray", 700).hex,
            },
            "QPushButton:hover, QPushButton:pressed": {
                "background-color": Color("blue", 100).hex,
                "border": f'1px solid {Color("blue", 300).hex}',
            },
        }

        return stylesheet_dict_to_str(style)


class Icon(QSvgWidget):
    def __init__(self, qrc_icon: str):
        """
        Initialises the icon.
        :param qrc_icon: The path to the resource icon.
        """
        super().__init__()
        self.qrc_icon = qrc_icon

        self.setMaximumSize(30, 30)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setStyleSheet("QSvgWidget { background: transparent }")

        self.renderer().load(self.svg_bytes)

    @property
    def svg_bytes(self) -> PySide6.QtCore.QByteArray:
        """
        Loads the icon and replace its colour.
        :return: The QByteArray instance.
        """
        f = QFile(self.qrc_icon)
        f.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(f)
        svg_data = stream.readAll()
        f.close()

        # replace colours with default
        svg_data = svg_data.replace("#3a3a38", Color("blue", 500).hex)
        svg_data = svg_data.replace("#ed8733", Color("blue", 500).hex)
        svg_data = svg_data.replace("#f8db8f", Color("blue", 200).hex)
        # noinspection PyTypeChecker
        return QByteArray(svg_data)


class TitleLabel(QLabel):
    def __init__(self, title: str):
        """
        Initialises the button title.
        :param title: The button title.
        """
        super().__init__()

        self.setText(title)
        self.setMaximumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(
            stylesheet_dict_to_str(
                {
                    "QLabel": {
                        "background": "transparent",
                        "color": Color("gray", 800).hex,
                        "font-size": "16px",
                    }
                }
            )
        )


class DescriptionLabel(QLabel):
    def __init__(self, description: str):
        """
        Initialises the button description.
        :param description: The button description.
        """
        super().__init__()

        self.setText(description)
        self.setMaximumHeight(15)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setStyleSheet(
            stylesheet_dict_to_str(
                {
                    "QLabel": {
                        "background": "transparent",
                        "color": Color("gray", 500).hex,
                    }
                }
            )
        )
