from typing import TYPE_CHECKING

import PySide6
from PySide6.QtGui import QFont, QFontMetrics, QPen, Qt, QTextOption

from pywr_editor.style import Color

from ..base_reservoir import BaseReservoir

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class VirtualStorage(BaseReservoir):
    is_pywr = True

    def __init__(self, parent: "SchematicNode", inside_label: str = "V"):
        """
        Initialises the class for a virtual storage node.
        :param parent: The schematic item.
        :param inside_label: The 1-letter label to write inside the shape.
        """
        super().__init__(
            parent=parent,
            fill=Color("sky", 200),
            outline=Color("sky", 700),
            label=Color("sky", 700),
        )
        self.inside_label = inside_label

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        super().paint(painter, option, widget)

        font = QFont()
        # font.setWeight(QFont.Bold)
        font.setPixelSize(12)
        painter.setFont(font)
        color = Color("sky", 900).qcolor
        painter.setPen(QPen(color))
        painter.setBrush(color)

        # font box
        font_box = QFontMetrics(font).boundingRect(self.inside_label)
        font_box.moveTo(-3 if font_box.width() <= 7 else -5, -5)
        font_box.setWidth(font_box.width() + 2)

        # text
        text_options = QTextOption()
        text_options.setAlignment(Qt.AlignmentFlag.AlignCenter)
        painter.drawText(font_box, self.inside_label, text_options)
