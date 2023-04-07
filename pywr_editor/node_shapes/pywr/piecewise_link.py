from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class PiecewiseLink(Circle):
    is_pywr = True

    def __init__(self, parent: "SchematicNode"):
        """
        Initialises a link node.
        :param parent: The schematic item group.
        """
        super().__init__(
            parent=parent,
            fill=Color("red", 200),
            outline=Color("red", 600),
            label=Color("red", 700),
            icon=IconProps(
                name=":schematic/cost",
                fill=Color("red", 700),
                outline=Color("red", 500),
            ),
        )
