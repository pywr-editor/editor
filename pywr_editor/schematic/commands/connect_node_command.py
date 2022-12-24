from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtGui import QUndoCommand

from pywr_editor.model import NodeConfig
from pywr_editor.utils import Logging

from ..edge import Edge

if TYPE_CHECKING:
    from pywr_editor.schematic import Schematic


class ConnectNodeCommand(QUndoCommand):
    def __init__(
        self,
        schematic: "Schematic",
        source_node_name: str,
        target_node_name: str,
    ):
        """
        Initialises the connect node command.
        :param schematic: The Schematic instance.
        :param source_node_name: The name of the source node.
        :param target_node_name: The name of the target node.
        :return: None
        """
        super().__init__()

        self.logger = Logging().logger(self.__class__.__name__)
        self.schematic = schematic
        self.app = self.schematic.app
        self.model_config = self.schematic.model_config

        self.source_node: NodeConfig = (
            self.model_config.nodes.get_node_config_from_name(
                source_node_name, as_dict=False
            )
        )
        self.target_node: NodeConfig = (
            self.model_config.nodes.get_node_config_from_name(
                target_node_name, as_dict=False
            )
        )
        # To properly restore, if the edge is changed (for ex. a Slot is added),
        # store the edge configuration for the undo command
        self.edge_config: list[str | int] | None = None
        self.setText("connect node")
        self.make_obsolete = False

    def redo(self) -> None:
        """
        Connect the node.
        :return: None
        """
        # edge is added for the first time
        if self.edge_config is None:
            if self.model_config.edges.add(
                source_node_name=self.source_node.name,
                target_node_name=self.target_node.name,
            ):
                self.logger.debug(
                    f"Added edge: [{self.source_node.name},"
                    + f"{self.target_node.name}]"
                )
        # restore edge delete with undo command
        else:
            if self.model_config.edges.add(*self.edge_config):
                self.logger.debug(f"Restored edge: {self.edge_config}")
            else:
                # When a node is renamed after the edge is deleted, its edge cannot
                # be restored. This also ensures consistency with all commands
                self.logger.debug(
                    f"Operation for '{self.source_node.name}' and "
                    + f"'{self.target_node.name}' is now obsolete"
                )
                # command cannot be make obsolete and removed from stack in redo().
                # Call undo() with delay as workaround
                self.make_obsolete = True
                QTimer.singleShot(200, self.app.undo_stack.undo)
                return

        self.schematic.scene.addItem(
            Edge(
                source=self.schematic.schematic_items[self.source_node.name],
                target=self.schematic.schematic_items[self.target_node.name],
                hide_arrow=self.app.editor_settings.are_edge_arrows_hidden,
            )
        )
        self.app.status_message.emit(
            f"Connected {self.source_node.name} to {self.target_node.name}"
        )
        self.app.components_tree.reload()

    def undo(self) -> None:
        """
        Disconnect the nodes that were previously connected with the redo command.
        :return: None
        """
        if self.make_obsolete:
            self.setObsolete(True)
            return

        # store the edge so that it can be restored later
        self.edge_config, _ = self.model_config.edges.find_edge(
            source_node_name=self.source_node.name,
            target_node_name=self.target_node.name,
        )

        # remove edge from model config
        self.model_config.edges.delete(
            source_node_name=self.source_node.name,
            target_node_name=self.target_node.name,
        )
        self.logger.debug(f"Deleted edge: {self.edge_config}")

        # remove edge from the edges list for the source node
        node_item = self.schematic.schematic_items[self.source_node.name]
        edge_to_delete = node_item.delete_edge(
            node_name=self.target_node.name, edge_type="target"
        )

        # remove edge from the edges list for the target node
        node_item = self.schematic.schematic_items[self.target_node.name]
        node_item.delete_edge(
            node_name=self.source_node.name, edge_type="source"
        )

        # remove graphic item from the schematic
        if edge_to_delete is not None:
            self.schematic.scene.removeItem(edge_to_delete)
        # object is still instantiated
        del edge_to_delete

        # update status bar and tree
        self.app.status_message.emit(
            f'Deleted edge from "{self.source_node.name}" to "{self.target_node.name}"'
        )
        self.app.components_tree.reload()
