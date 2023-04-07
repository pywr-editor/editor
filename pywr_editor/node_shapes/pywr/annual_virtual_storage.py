from typing import TYPE_CHECKING

from .virtual_storage import VirtualStorage

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class AnnualVirtualStorage(VirtualStorage):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the class for an annual virtual storage node.
        :param parent: The schematic item.
        """
        super().__init__(parent=parent, inside_label="Y")
