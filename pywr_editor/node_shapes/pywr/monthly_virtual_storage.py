from typing import TYPE_CHECKING

from .pywr_node import PywrNode
from .virtual_storage import VirtualStorage

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class MonthlyVirtualStorage(VirtualStorage, PywrNode):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the class for a monthly virtual storage node.
        :param parent: The schematic item.
        """
        super().__init__(parent=parent, inside_label="M")
