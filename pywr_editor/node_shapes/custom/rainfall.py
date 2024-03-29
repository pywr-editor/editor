from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class Rainfall(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the class for a pumping station node.
        :param parent: The parent node
        :return None
        """
        super().__init__(
            parent=parent,
            fill=Color("sky", 200),
            outline=Color("sky", 500),
            label=Color("sky", 600),
            icon=IconProps(
                name=":schematic/rainfall",
                fill=Color("sky", 600),
                outline=Color("sky", 700),
            ),
        )
