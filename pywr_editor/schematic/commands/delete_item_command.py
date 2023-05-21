from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

from pywr_editor.model import BaseShape, NodeConfig
from pywr_editor.utils import Logging

from ..node import SchematicNode
from ..shapes.abstract_schematic_shape import AbstractSchematicShape

if TYPE_CHECKING:
    from pywr_editor.schematic import AbstractSchematicItem, Schematic


class DeleteItemCommand(QUndoCommand):
    """
    Undo command used to undo/redo schematic items (nodes, edges and shapes)
    deletion.
    """

    def __init__(
        self,
        schematic: "Schematic",
        selected_items: list["AbstractSchematicItem"],
    ):
        """
        Initialise the command to delete nodes, edges and shapes.
        :param schematic: The Schematic instance.
        :param selected_items: The list of selected schematic item instances to delete.
        :return: None
        """
        super().__init__()

        self.logger = Logging().logger(self.__class__.__name__)
        self.schematic = schematic
        self.model_config = self.schematic.model_config
        self.deleted_node_names = [
            node.name for node in selected_items if isinstance(node, SchematicNode)
        ]
        self.deleted_shape_ids: list[str] = [
            shape.id
            for shape in selected_items
            if isinstance(shape, AbstractSchematicShape)
        ]
        total_items = len(self.deleted_node_names) + len(self.deleted_shape_ids)
        prefix = "item" if total_items == 1 else "items"
        self.setText(f"delete {total_items} {prefix}")

        # collect the nodes configuration to delete. This is updated in the redo
        # command and emptied in the undo command to ensure that when the configuration
        # is restored, this always contains the latest changes
        self.deleted_node_configs: list[NodeConfig] = []

        # lists of deleted edges (nodes and slots) collected in the redo command. Note
        # that, if a node in an edge is renamed, and the operation is undone, the edge
        # is not restored because the node was changed
        self.deleted_edges: list[list[str | int]] = []

        # list of annotation shapes collected in the redo command
        self.deleted_shape_configs: list[BaseShape] = []

    def redo(self) -> None:
        """
        Delete the schematic items from the schematic and model configuration.
        :return: None
        """
        # when the user deletes a node for the first time, then undoes and redoes
        # the action, the node name must be updated, in case the item was renamed
        if self.deleted_node_configs:
            self.deleted_node_names = [
                node_config.name for node_config in self.deleted_node_configs
            ]

        self.deleted_edges = []  # store the deleted edges
        self.deleted_node_configs = []  # always empty this after undo
        for node_name in self.deleted_node_names:
            node_config = self.model_config.nodes.config(node_name, as_dict=False)
            self.deleted_node_configs.append(node_config)

            model_edges = self.schematic.delete_node(node_name)
            self.deleted_edges += model_edges
            self.logger.debug(f"Deleted node with config: {node_config.props}")
        self.logger.debug(f"Deleted edges: {self.deleted_edges}")

        # delete shapes
        self.deleted_shape_configs = []  # always empty this after redo
        for shape_id in self.deleted_shape_ids:
            shape_config = self.model_config.shapes.find_shape(shape_id)
            self.deleted_shape_configs.append(shape_config)

            self.schematic.delete_shape(shape_config.id)
            self.logger.debug(f"Deleted shape with config: {shape_config.shape_dict}")

        # status message
        edges_count = len(self.deleted_edges)
        item_count = len(self.deleted_node_configs) + len(self.deleted_shape_configs)
        status_message = "Deleted "
        if item_count == 1:
            status_message += "1 schematic item"
        elif item_count > 1:
            status_message += f"{item_count} schematic items"

        if edges_count == 1:
            status_message += " and one edge"
        elif edges_count > 1:
            status_message += f" and {edges_count} edges"

        self.schematic.app.status_message.emit(status_message)

        # update widgets
        self.schematic.app.components_tree.reload()
        self.schematic.reload()

    def undo(self) -> None:
        """
        Restores the deleted nodes, edges and shapes into the schematic.
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

        # add shapes
        for shape_config in self.deleted_shape_configs:
            self.model_config.shapes.update(
                shape_id=shape_config.id, shape_dict=shape_config.shape_dict
            )
            self.logger.debug(f"Added shape with config: {shape_config}")

        # emit the status message
        item_count = len(self.deleted_node_configs) + len(self.deleted_shape_configs)
        suffix_node = "item" if item_count == 1 else "items"
        status_message = f"Restored {item_count} schematic {suffix_node}"
        if restored_edges > 0:
            suffix_edges = "edge" if restored_edges == 1 else "edges"
            status_message += f" and {restored_edges} {suffix_edges}"

        self.schematic.app.status_message.emit(status_message)
        self.logger.debug(status_message)

        # reload widgets
        self.schematic.reload()
        self.schematic.app.components_tree.reload()
