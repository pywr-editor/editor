from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

from .edge import TempEdge

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


@dataclass
class ConnectingNodeProps:
    enabled: bool = False
    """ Whether the connection is taking place """
    temp_edge: TempEdge | None = None
    """ The instance of the temporary edge """
    source_node: Union["SchematicNode", None] = None
    """ The instance of the schematic source node """

    def reset(self):
        """
        Resets the properties.
        """
        self.enabled = False
        self.temp_edge = None
        self.source_node = None
