from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class Evaporation(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the class for a pumping station node.
        :param parent: The parent node
        :return None
        """
        super().__init__(
            parent=parent,
            fill=Color("orange", 200),
            outline=Color("orange", 500),
            label=Color("orange", 600),
            icon=IconProps(
                name=":schematic/evaporation",
                fill=Color("orange", 600),
                outline=Color("orange", 700),
            ),
        )
