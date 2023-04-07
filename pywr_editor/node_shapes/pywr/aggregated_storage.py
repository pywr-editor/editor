from typing import TYPE_CHECKING

import PySide6

from pywr_editor.style import Color

from ..base_node import BaseNode
from ..base_reservoir import BaseReservoir

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class AggregatedStorage(BaseNode):
    is_pywr = True

    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the class for a node output.
        """
        super().__init__(parent)

        self.label = Color("blue", 500)
        self.node = self

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        highlight = self.hover or self.isSelected()

        # reservoir 1
        painter.scale(0.8, 0.8)
        painter.translate(-2, -5)
        BaseReservoir.draw_reservoir(
            painter=painter,
            pen_width=self.outline_width,
            bbox=self.boundingRect(),
            size=self.size,
            fill_color=Color("blue", 200),
            outline_color=Color("blue", 600),
            highlight=highlight,
            focus_color=Color("blue", 300),
        )

        # reservoir 2
        painter.scale(0.9, 0.9)
        painter.translate(7, 8)
        BaseReservoir.draw_reservoir(
            painter=painter,
            pen_width=self.outline_width,
            bbox=self.boundingRect(),
            size=self.size,
            fill_color=Color("violet", 200),
            outline_color=Color("violet", 600),
            highlight=highlight,
            focus_color=Color("violet", 300),
        )
