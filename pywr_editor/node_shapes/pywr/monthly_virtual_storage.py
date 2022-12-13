from .virtual_storage import VirtualStorage
from .pywr_node import PywrNode
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class MonthlyVirtualStorage(VirtualStorage, PywrNode):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the class for a monthly virtual storage node.
        :param parent: The schematic item.
        """
        super().__init__(parent=parent, inside_label="M")
