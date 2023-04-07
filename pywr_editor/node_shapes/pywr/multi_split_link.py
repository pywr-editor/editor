from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class MultiSplitLink(Circle):
    is_pywr = True

    def __init__(self, parent: "SchematicNode"):
        """
        Initialises a link node.
        :param parent: The schematic item group.
        """
        super().__init__(
            parent=parent,
            fill=Color("stone", 200),
            outline=Color("stone", 500),
            label=Color("stone", 600),
            icon=IconProps(
                name=":schematic/split",
                fill=Color("stone", 700),
                outline=Color("stone", 500),
            ),
        )
