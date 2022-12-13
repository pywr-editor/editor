from ..circle import Circle
from .pywr_node import PywrNode
from pywr_editor.style import Color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class Link(Circle, PywrNode):
    def __init__(self, parent: "SchematicItem"):
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
