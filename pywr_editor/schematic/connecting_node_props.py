from dataclasses import dataclass

from .edge import TempEdge
from .schematic_item import SchematicItem


@dataclass
class ConnectingNodeProps:
    enabled: bool = False
    """ Whether the connection is taking place """
    temp_edge: TempEdge | None = None
    """ The instance of the temporary edge """
    source_node: SchematicItem | None = None
    """ The instance of the schematic source node """

    def reset(self):
        """
        Resets the properties.
        """
        self.enabled = False
        self.temp_edge = None
        self.source_node = None
