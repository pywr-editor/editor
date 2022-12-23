from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps
from .pywr_node import PywrNode

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class LossLink(Circle, PywrNode):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the class for a leak node.
        :param parent: The parent node
        :return None
        """
        super().__init__(
            parent=parent,
            fill=Color("gray", 200),
            outline=Color("gray", 500),
            label=Color("gray", 600),
            icon=IconProps(
                name=":schematic/leak",
                fill=Color("gray", 600),
                outline=Color("gray", 700),
                padding=2,
            ),
        )
