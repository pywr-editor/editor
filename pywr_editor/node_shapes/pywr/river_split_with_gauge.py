from typing import TYPE_CHECKING

from .river_gauge import RiverGauge

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class RiverSplitWithGauge(RiverGauge):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape.
        :param parent: The schematic item group.
        """
        super().__init__(parent=parent)
