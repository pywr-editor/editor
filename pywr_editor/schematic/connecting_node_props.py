from dataclasses import dataclass

from .edge import TempEdge
from .node import SchematicNode


@dataclass
class ConnectingNodeProps:
    enabled: bool = False
    """ Whether the connection is taking place """
    temp_edge: TempEdge | None = None
    """ The instance of the temporary edge """
    source_node: SchematicNode | None = None
    """ The instance of the schematic source node """

    def reset(self):
        """
        Resets the properties.
        """
        self.enabled = False
        self.temp_edge = None
        self.source_node = None
