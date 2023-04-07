from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..base_reservoir import BaseReservoir

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class Storage(BaseReservoir):
    is_pywr = True

    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the class for a node output.
        """
        super().__init__(
            parent=parent,
            fill=Color("blue", 200),
            outline=Color("blue", 600),
            label=Color("blue", 500),
        )
