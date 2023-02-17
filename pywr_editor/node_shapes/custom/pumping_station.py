from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class PumpingStation(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the class for a pumping station node.
        :param parent: The parent node
        :return None
        """
        super().__init__(
            parent=parent,
            fill=Color("red", 200),
            outline=Color("red", 500),
            label=Color("red", 600),
            icon=IconProps(
                name=":schematic/pumping-station",
                fill=Color("red", 600),
                outline=Color("red", 700),
                padding=2,
            ),
        )
