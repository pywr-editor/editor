from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps
from .pywr_node import PywrNode

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class DelayNode(Circle, PywrNode):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises a delay node.
        :param parent: The schematic item group.
        """
        super().__init__(
            parent=parent,
            fill=Color("violet", 100),
            outline=Color("violet", 400),
            label=Color("violet", 600),
            icon=IconProps(
                name=":schematic/delay",
                fill=Color("violet", 700),
                outline=Color("violet", 400),
            ),
        )
