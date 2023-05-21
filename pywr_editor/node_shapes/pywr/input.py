from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class Input(Circle):
    is_pywr = True

    def __init__(self, parent: "SchematicNode"):
        """
        Initialises a link node.
        :param parent: The schematic item group.
        """
        super().__init__(
            parent=parent,
            fill=Color("green", 200),
            outline=Color("green", 600),
            label=Color("green", 700),
            icon=IconProps(
                name=":schematic/input",
                fill=Color("green", 700),
                outline=Color("green", 500),
            ),
        )
