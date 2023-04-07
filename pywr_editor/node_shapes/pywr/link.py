from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..circle import Circle

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class Link(Circle):
    is_pywr = True

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
        )
