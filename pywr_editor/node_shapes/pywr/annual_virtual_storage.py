from typing import TYPE_CHECKING

from .pywr_node import PywrNode
from .virtual_storage import VirtualStorage

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class AnnualVirtualStorage(VirtualStorage, PywrNode):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the class for an annual virtual storage node.
        :param parent: The schematic item.
        """
        super().__init__(parent=parent, inside_label="Y")
