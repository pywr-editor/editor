from typing import TYPE_CHECKING

from pywr_editor.style import Color

from ..base_reservoir import BaseReservoir
from .pywr_node import PywrNode

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class Storage(BaseReservoir, PywrNode):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the class for a node output.
        """
        super().__init__(
            parent=parent,
            fill=Color("blue", 200),
            outline=Color("blue", 600),
            label=Color("blue", 500),
        )
