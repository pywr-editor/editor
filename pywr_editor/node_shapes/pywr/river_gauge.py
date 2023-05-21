from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class RiverGauge(Circle):
    is_pywr = True

    def __init__(self, parent: "SchematicNode"):
        """
        Initialises a link node.
        :param parent: The schematic item group.
        """
        super().__init__(
            parent=parent,
            fill=Color("blue", 200),
            outline=Color("blue", 600),
            label=Color("blue", 700),
            icon=IconProps(
                name=":schematic/gauge",
                fill=Color("blue", 700),
                outline=Color("blue", 500),
            ),
        )
