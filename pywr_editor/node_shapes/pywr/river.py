from ..circle import Circle
from ..svg_icon import IconProps
from .pywr_node import PywrNode
from pywr_editor.style import Color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class River(Circle, PywrNode):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises a link node.
        :param parent: The schematic item group.
        """
        super().__init__(
            parent=parent,
            fill=Color("blue", 200),
            outline=Color("blue", 600),
            label=Color("blue", 700),
            icon=IconProps(
                name=":schematic/water",
                fill=Color("blue", 700),
                outline=Color("blue", 500),
            ),
        )
