import sys
from datetime import datetime
from typing import TYPE_CHECKING, Union

import pywr
from PySide6.QtCore import QSize
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from pywr_editor.style import Color
from pywr_editor.widgets import PushIconButton

from .about_dialog_style_sheet import about_dialog_stylesheet
from .legal_dialog import LegalDialog

if TYPE_CHECKING:
    from .about_button import AboutButton


class AboutDialog(QDialog):
    def __init__(self, parent: Union["AboutButton", None] = None):
        """
        Initialises the dialog.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("About Pywr editor")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(about_dialog_stylesheet())

        width, height = (470, 220)
        self.setMaximumSize(width, height)
        self.setMinimumSize(width, height)

        # Text
        from pywr_editor import __build_date__, __version__

        build_date = datetime.strptime(__build_date__, "%Y-%m-%d").strftime(
            "%d %b %Y"
        )

        # flake8: noqa
        text = f"""<div style="font-weight:bold; font-size:16px">Pywr editor {__version__}</div>
        <div style="margin-top:5px">Build on: {build_date}</div>
        <div style="margin-top:5px">Runtime version: Python {sys.version}</div>
        <div style="margin-top:2px;margin-bottom:25px">Pywr version: {pywr.__version__}</div>

        <p>Copyright (C) 2021-{datetime.now().strftime('%Y')}  Stefano Simoncelli</p>
    
        <p>This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.</p>
    
        <p>This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.</p>
        """
        content = QLabel(text)
        content.setWordWrap(True)

        # Legal notices
        button_style = (
            f"background: none; border: 0; padding: 0; margin-right: 10px; "
            + f"color: {Color('blue', 600).hex}; text-decoration: underline;"
            + "text-align: left;"
        )
        legal_dialog_link = QPushButton("Legal notices")
        legal_dialog_link.setStyleSheet(button_style)
        # noinspection PyUnresolvedReferences
        legal_dialog_link.clicked.connect(self.show_legal_dialog)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(content)
        content_layout.addWidget(legal_dialog_link)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(self.reject)

        # Logo + legal widgets layout
        logo_layout = QVBoxLayout()
        logo = PushIconButton(icon=":logos/normal", icon_size=QSize(70, 70))
        logo_layout.addWidget(logo)
        logo_layout.addStretch()
        logo.setStyleSheet("background: none; border: none; padding: 0px 6px")

        top_layout = QHBoxLayout()
        top_layout.addLayout(logo_layout)
        top_layout.addLayout(content_layout)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def show_legal_dialog(self) -> None:
        """
        Shows the legal dialog.
        :return: None
        """
        dialog = LegalDialog(self)
        dialog.show()
