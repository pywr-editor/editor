from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps
from .pywr_node import PywrNode

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class Input(Circle, PywrNode):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises a link node.
        :param parent: The schematic item group.
        """
        super().__init__(
            parent=parent,
            fill=Color("green", 200),
            outline=Color("green", 600),
            label=Color("green", 700),
            icon=IconProps(
                name=":schematic/input",
                fill=Color("green", 700),
                outline=Color("green", 500),
            ),
        )
