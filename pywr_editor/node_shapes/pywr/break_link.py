from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps
from .pywr_node import PywrNode

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class BreakLink(Circle, PywrNode):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises a break link node.
        :param parent: The schematic item group.
        """
        super().__init__(
            parent=parent,
            fill=Color("gray", 200),
            outline=Color("gray", 500),
            label=Color("gray", 600),
            icon=IconProps(
                name=":schematic/break-link",
                fill=Color("gray", 700),
                outline=Color("gray", 500),
            ),
        )
