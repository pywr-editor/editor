from ..circle import Circle
from ..svg_icon import IconProps
from .pywr_node import PywrNode
from pywr_editor.style import Color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class MultiSplitLink(Circle, PywrNode):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises a link node.
        :param parent: The schematic item group.
        """
        super().__init__(
            parent=parent,
            fill=Color("stone", 200),
            outline=Color("stone", 500),
            label=Color("stone", 600),
            icon=IconProps(
                name=":schematic/split",
                fill=Color("stone", 700),
                outline=Color("stone", 500),
            ),
        )
