from PySide6.QtGui import QUndoCommand
from typing import TYPE_CHECKING
from pywr_editor.model import NodeConfig
from pywr_editor.utils import Logging
from ..edge import Edge

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem, Schematic


class DeleteNodeCommand(QUndoCommand):
    def __init__(
        self, schematic: "Schematic", selected_nodes: list["SchematicItem"]
    ):
        """
        Initialises the delete node command.
        :param selected_nodes: The list of selected nodes to delete.
        :return: None
        """
        super().__init__()

        self.logger = Logging().logger(self.__class__.__name__)
        self.schematic = schematic
        self.model_config = self.schematic.model_config
        # self.nodes = selected_nodes
        self.deleted_node_configs: dict[str, NodeConfig] = {}

        # collect the node and edge configuration
        self.deleted_node_configs = {
            node.name: self.model_config.nodes.get_node_config_from_name(
                node.name
            )
            for node in selected_nodes
        }
        self.deleted_edges: list[list[str]] = []

    def redo(self) -> None:
        """
        Deletes the nodes and their edges from the schematic and model configuration.
        :return: None
        """
        self.deleted_edges = []
        for node_name, node_config in self.deleted_node_configs.items():
            # find the node shape on the schematic
            node_item = self.schematic.schematic_items[node_name]

            # delete edges on the schematic when node is source node
            for c_node in node_item.connected_nodes["target_nodes"]:
                for ei, edge_item in enumerate(c_node.edges):
                    if edge_item.source.name == node_item.name:
                        self.delete_edge(edge_item)
                        del c_node.edges[ei]
                        break

            # delete edges on the schematic when node is target node
            for c_node in node_item.connected_nodes["source_nodes"]:
                for ei, edge_item in enumerate(c_node.edges):
                    if edge_item.target.name == node_item.name:
                        self.delete_edge(edge_item)
                        del c_node.edges[ei]
                        break

            # remove graphic nodes in schematic and model config
            node_config = self.model_config.nodes.get_node_config_from_name(
                node_name
            )
            self.model_config.nodes.delete(node_name)

            del self.schematic.schematic_items[node_name]
            self.schematic.scene.removeItem(node_item)
            self.logger.debug(f"Deleted node with config: {node_config}")

        # status message
        edges_count = len(self.deleted_edges)
        if len(self.deleted_node_configs) == 1:
            status_message = (
                f"Deleted node '{list(self.deleted_node_configs.keys())[0]}'"
            )
            if edges_count == 1:
                status_message += " and its edge"
            if edges_count > 1:
                status_message += f" and its {edges_count} edges"
        else:
            status_message = (
                f"Deleted {len(self.deleted_node_configs)} nodes and "
                + f"{edges_count} edges"
            )
        # noinspection PyUnresolvedReferences
        self.schematic.app.status_message.emit(status_message)
        self.logger.debug(status_message)

        # update widgets
        self.schematic.app.components_tree.reload()
        self.schematic.reload()

    def delete_edge(self, edge_item: Edge) -> None:
        """
        Deletes the edge from the schematic and model configuration.
        :param edge_item: The schematic Edge instance.
        :return: None
        """
        self.schematic.scene.removeItem(edge_item)
        # delete edge from model config
        edge = [edge_item.source.name, edge_item.target.name]
        self.model_config.edges.delete(edge)
        self.deleted_edges.append(edge)
        self.logger.debug(f"Deleted edge [{edge[0]}, {edge[1]}]")

    def undo(self) -> None:
        """
        Restores the deleted nodes and edges into the schematic.
        :return: None
        """
        # add nodes
        for node_config in self.deleted_node_configs.values():
            self.logger.debug(f"Restoring node config: {node_config}")
            self.model_config.nodes.add(node_config)

        # add edges
        for edge in self.deleted_edges:
            self.logger.debug(f"Restoring edge: [{edge[0]}, {edge[1]}]")
            self.model_config.edges.add(edge[0], edge[1])

        # emit the status message
        status_message = (
            f"Restored {len(self.deleted_node_configs)} node(s) and "
            + f"{len(self.deleted_edges)} edge(s)"
        )
        self.schematic.app.status_message.emit(status_message)
        self.logger.debug(status_message)

        # reload widgets
        self.schematic.reload()
        self.schematic.app.components_tree.reload()
