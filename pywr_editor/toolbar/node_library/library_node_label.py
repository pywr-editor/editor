from typing import TYPE_CHECKING
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSimpleTextItem,
)
from pywr_editor.style import Color

if TYPE_CHECKING:
    from .library_node import LibraryNode


class LibraryNodeLabel(QGraphicsSimpleTextItem):
    def __init__(
        self,
        parent: "LibraryNode",
        name: str,
        color: Color,
    ):
        """
        Initialises the label.
        :param parent: The parent graphic item.
        :param name: The node name.
        :param color: The node label color.
        """
        super().__init__(parent)
        self.parent = parent
        self.symbol = parent.node

        self.setFont(self.font)
        self.setText(name)
        self.setBrush(color.qcolor)

        self.setAcceptHoverEvents(False)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setX(24)
        self.setY(-self.boundingRect().height() / 2)

    @property
    def font(self) -> QFont:
        """
        Returns the font.
        :return: None
        """
        font = QFont()
        font.setPixelSize(17)
        return font
