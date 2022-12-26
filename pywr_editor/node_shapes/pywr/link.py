from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle
from .pywr_node import PywrNode

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class Link(Circle, PywrNode):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises a link node.
        :param parent: The schematic item group.
        """
        super().__init__(
            parent=parent,
            fill=Color("slate", 200),
            outline=Color("slate", 500),
            label=Color("slate", 700),
            # icon=IconProps(
            #     name='link',
            #     fill=Color('slate', 700),
            #     outline=Color('slate', 500),
            # )
        )
