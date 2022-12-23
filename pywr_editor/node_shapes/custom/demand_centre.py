from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class DemandCentre(Circle):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the class for a demand centre node.
        :param parent: The parent node
        :return None
        """
        super().__init__(
            parent=parent,
            fill=Color("amber", 200),
            outline=Color("amber", 600),
            icon=IconProps(
                name=":schematic/demand-centre",
                outline=Color("amber", 700),
                fill=Color("amber", 700),
                padding=5,
            ),
        )
