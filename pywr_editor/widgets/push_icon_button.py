from typing import Literal
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QPushButton, QSizePolicy


class PushIconButton(QPushButton):
    def __init__(
        self,
        icon: str | QIcon,
        icon_size=None,
        label: str = "",
        small: bool = False,
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
            icon = QIcon(icon)

        self.setText(label)
        self.setIcon(icon)
        if icon_size is None:
            if small:
                icon_size = QSize(14, 14)
            else:
                icon_size = QSize(16, 16)
        self.setIconSize(icon_size)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        if position == "right":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        if small:
            self.setStyleSheet("PushIconButton {padding: 4px 8px}")
        else:
            self.setStyleSheet("PushIconButton {padding: 6px 15px}")
