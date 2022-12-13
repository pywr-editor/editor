from .river_gauge import RiverGauge
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class RiverSplitWithGauge(RiverGauge):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the shape.
        :param parent: The schematic item group.
        """
        super().__init__(parent=parent)
