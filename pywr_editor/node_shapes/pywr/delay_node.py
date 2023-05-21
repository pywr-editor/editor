from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class DelayNode(Circle):
    is_pywr = True

    def __init__(self, parent: "SchematicNode"):
        """
        Initialises a delay node.
        :param parent: The schematic item group.
        """
        super().__init__(
            parent=parent,
            fill=Color("violet", 100),
            outline=Color("violet", 400),
            label=Color("violet", 600),
            icon=IconProps(
                name=":schematic/delay",
                fill=Color("violet", 700),
                outline=Color("violet", 400),
            ),
        )
