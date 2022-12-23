import re
from typing import TYPE_CHECKING, Union

import PySide6
from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QGraphicsItemGroup

from pywr_editor.style import Color

if TYPE_CHECKING:
    from pywr_editor.node_shapes import DummyGraphicsItem
    from pywr_editor.schematic import SchematicItem


class BaseNode(QGraphicsItemGroup):
    size: list[int] = [24, 24]

    def __init__(
        self,
        parent: Union["SchematicItem", "DummyGraphicsItem"],
        fill: Color | None = None,
        outline: Color | None = None,
        label: Color | None = None,
    ):
        """
        Initialises the class for a generic shape.
        :param parent: The parent node.
        :param fill: The fill color.
        :param outline: The outline color.
        :param label: The label_color color.
        :return None
        """
        super().__init__(parent)

        self.x = parent.x
        self.y = parent.y

        self.parent = parent
        self.outline_width = 1
        self.fill = fill
        self.outline = outline
        self.label = label
        self.hover = False

        if self.fill is None:
            self.fill = Color(name="gray", shade=400)
        if self.outline is None:
            self.outline = Color(name="gray", shade=800)
        if self.label is None:
            self.label = self.outline

    def boundingRect(self) -> PySide6.QtCore.QRectF:
        """
        Defined the node bounding rectangle.
        :return: The rectangle.
        """
        return QRectF(
            -self.size[0] / 2 - self.outline_width,
            -self.size[1] / 2 - self.outline_width,
            self.size[0] + self.outline_width * 2,
            self.size[1] + self.outline_width * 2,
        )

    @property
    def focus_color(self) -> Color:
        """
        Returns the fill color when the shape is selected or hovered.
        :return: The Color
        """
        delta_shade = 100
        if self.fill.shade == 900:
            delta_shade = -400

        return self.fill.change_shade(self.fill.shade + delta_shade)

    @property
    def name(self) -> str:
        """
        Converts the class name to the node name. For example "AggregatedNode" returns
        "Aggregated".
        :return: The formatted name.
        """
        node_class_name = self.__class__.__name__
        label_list = re.findall("[A-Z][^A-Z]*", node_class_name)
        label_list = [name.lower() for name in label_list]
        if len(label_list) <= 1:
            new_label = node_class_name.title()
        else:
            label_list[0] = label_list[0].title()
            new_label = " ".join(label_list)

        return new_label.replace("node", "")
