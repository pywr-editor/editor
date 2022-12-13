from ..circle import Circle
from ..svg_icon import IconProps
from pywr_editor.style import Color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class PumpingStation(Circle):
    def __init__(self, parent: "SchematicItem"):
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
