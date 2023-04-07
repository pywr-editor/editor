from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from ..svg_icon import IconProps

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class LossLink(Circle):
    is_pywr = True

    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the class for a leak node.
        :param parent: The parent node
        :return None
        """
        super().__init__(
            parent=parent,
            fill=Color("gray", 200),
            outline=Color("gray", 500),
            label=Color("gray", 600),
            icon=IconProps(
                name=":schematic/leak",
                fill=Color("gray", 600),
                outline=Color("gray", 700),
                padding=2,
            ),
        )
