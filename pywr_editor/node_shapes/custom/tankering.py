from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class Tankering(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the class for a leak node.
        :param parent: The parent node
        :return None
        """
        super().__init__(
            parent=parent,
            fill=Color("pink", 200),
            outline=Color("pink", 500),
            label=Color("pink", 600),
            icon=IconProps(
                name=":schematic/tankering",
                fill=Color("pink", 500),
                outline=Color("pink", 500),
                padding=2.5,
            ),
        )
