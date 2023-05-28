from typing import Literal

import qtawesome as qta
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QPushButton, QSizePolicy

from pywr_editor.style import Color, stylesheet_dict_to_str


class PushIconButton(QPushButton):
    def __init__(
        self,
        icon: str | QIcon,
        icon_size=None,
        label: str = "",
        small: bool = False,
        accent: bool = False,
        position: Literal["left", "right"] = "left",
        parent=None,
    ):
        """
        Renders a QPUshButton with an icon.
        :param icon: The icon path or QIcon instance.
        :param label: The button label. Optional.
        :param icon_size: The size of the icon. Default to QSize(16, 16).
        :param position: The icon position (left or right). Default to left.
        :param small: Whether to reduce the x-padding size. Default to False.
        :param parent: The parent widget. Optional.
        """
        super().__init__(parent=parent)

        if isinstance(icon, str):
            if "msc." in icon:
                props = (
                    dict(
                        color="white",
                        color_active="white",
                        color_disabled=Color("gray", 300).hex,
                    )
                    if accent
                    else {}
                )
                icon = qta.icon(icon, **props)
            else:
                icon = QIcon(icon)

        self.setText(label)
        self.setIcon(icon)
        if icon_size is None:
            icon_size = QSize(16, 16)
        self.setIconSize(icon_size)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        if position == "right":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        stylesheet = {"padding": "3px 4px" if small else "5px 5px"}
        if accent:
            stylesheet["color"] = "white"
            stylesheet["background"] = Color("blue", 500).hex
            stylesheet["border-color"] = Color("blue", 600).hex
            stylesheet[":hover"] = {
                "background": Color("blue", 600).hex,
                "border": f"1px solid {Color('blue', 600).hex}",
            }
            stylesheet[":disabled"] = {
                "background": Color("gray", 100).hex,
                "border": f"1px solid {Color('gray', 300).hex}",
                "color": Color("gray", 300).hex,
            }
        self.setStyleSheet(stylesheet_dict_to_str({"PushIconButton": stylesheet}))
