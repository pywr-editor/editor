from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

from pywr_editor.model import NodeConfig
from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from pywr_editor.schematic import Schematic, SchematicNode


class DeleteNodeCommand(QUndoCommand):
    def __init__(
        self, schematic: "Schematic", selected_nodes: list["SchematicNode"]
    ):
        """
        Initialises the delete node command.
        :param schematic: The Schematic instance.
        :param selected_nodes: The list of selected schematic node instances to delete.
        :return: None
        """
        super().__init__()

        self.logger = Logging().logger(self.__class__.__name__)
        self.schematic = schematic
        self.model_config = self.schematic.model_config

        # collect the node to delete. Internal dict gets updated by ref if the node
        # configuration is changed so that the restored node always contains the latest
        # changes
        self.deleted_node_configs: list[NodeConfig] = [
            self.model_config.nodes.get_node_config_from_name(
                node.name, as_dict=False
            )
            for node in selected_nodes
        ]
        # lists of deleted edges (nodes and slots) from the redo command. If a node
        # in an edge is renamed, and the operation is undone, the edge is not
        # restored because the node was changed
        self.deleted_edges: list[list[str | int]] = []

        total_nodes = len(self.deleted_node_configs)
        prefix = "node" if total_nodes == 1 else "nodes"
        self.setText(f"delete {total_nodes} {prefix}")

    def redo(self) -> None:
        """
        Deletes the nodes and their edges from the schematic and model configuration.
        :return: None
        """
        # delete node and store deleted edges
        self.deleted_edges = []
        for node_config in self.deleted_node_configs:
            node_name = node_config.name
            model_edges = self.schematic.delete_node(node_name)
            self.deleted_edges += model_edges
            self.logger.debug(f"Deleted node with config: {node_config.props}")
        self.logger.debug(f"Deleted edges: {self.deleted_edges}")

        # status message
        edges_count = len(self.deleted_edges)
        if len(self.deleted_node_configs) == 1:
            status_message = (
                f"Deleted node '{self.deleted_node_configs[0].name}'"
            )
            if edges_count == 1:
                status_message += " and its edge"
            elif edges_count > 1:
                status_message += f" and its {edges_count} edges"
        else:
            status_message = (
                f"Deleted {len(self.deleted_node_configs)} nodes and "
                + f"{edges_count} edges"
            )
        self.schematic.app.status_message.emit(status_message)

        # update widgets
        self.schematic.app.components_tree.reload()
        self.schematic.reload()

    def undo(self) -> None:
        """
        Restores the deleted nodes and edges into the schematic.
        :return: None
        """
        # add nodes
        for node_config in self.deleted_node_configs:
            self.model_config.nodes.add(node_config.props)
            self.logger.debug(f"Restored node config: {node_config.props}")

        # add edges
        restored_edges = 0
        for edge in self.deleted_edges:
            # check that the edge is still valid
            if self.model_config.edges.add(*edge):
                self.logger.debug(f"Restored edge: {edge}")
                restored_edges += 1

        # emit the status message
        suffix_node = "node" if len(self.deleted_node_configs) == 1 else "nodes"
        status_message = (
            f"Restored {len(self.deleted_node_configs)} {suffix_node}"
        )
        if restored_edges > 0:
            suffix_edges = "edge" if restored_edges == 1 else "edges"
            status_message += f" and {restored_edges} {suffix_edges}"

        self.schematic.app.status_message.emit(status_message)
        self.logger.debug(status_message)

        # reload widgets
        self.schematic.reload()
        self.schematic.app.components_tree.reload()
