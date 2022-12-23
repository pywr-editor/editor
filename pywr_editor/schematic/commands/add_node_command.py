from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

from pywr_editor.model import NodeConfig
from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from pywr_editor.schematic import Schematic


class AddNodeCommand(QUndoCommand):
    def __init__(
        self,
        schematic: "Schematic",
        added_node_dict: dict,
    ):
        """
        Initialises the delete node command.
        :param schematic: The Schematic instance.
        :param added_node_dict: The dictionary with the configuration of the node to
        add.
        :return: None
        """
        super().__init__()

        self.logger = Logging().logger(self.__class__.__name__)
        self.schematic = schematic
        self.added_node_dict = added_node_dict
        self.node_config: NodeConfig | None = None
        self.model_config = self.schematic.model_config
        self.deleted_edges: list[list[str | int]] = []
        self.setText("add new node")

    def redo(self) -> None:
        """
        Adds the node for the first time or restore it.
        :return: None
        """
        # add node for the first time
        if self.node_config is None:
            self.model_config.nodes.add(self.added_node_dict)
            self.node_config = (
                self.model_config.nodes.get_node_config_from_name(
                    self.added_node_dict["name"], as_dict=False
                )
            )
            # add the node to the schematic and model config
            self.schematic.add_node(node_props=self.added_node_dict)

            self.logger.debug(
                f"Added node to schematic with: {self.added_node_dict}"
            )
            status_message = (
                "Added new node of type "
                + f"'{self.node_config.humanise_node_type}'"
            )
        # restore deleted node
        else:
            # add node
            self.logger.debug(
                f"Restoring node config: {self.node_config.props}"
            )
            self.model_config.nodes.add(self.node_config.props)

            # add edges
            for edge in self.deleted_edges:
                self.logger.debug(f"Restoring edge: {edge}")
                self.model_config.edges.add(*edge)

            # emit the status message
            status_message = (
                f"Restored '{self.node_config.name}' and its "
                + f"{len(self.deleted_edges)} edge(s)"
            )

        self.schematic.app.status_message.emit(status_message)

        # reload widgets
        self.schematic.reload()
        self.schematic.app.components_tree.reload()

    def undo(self) -> None:
        """
        Removes the previously-added node.
        :return: None
        """
        node_name = self.node_config.name
        # delete node and edges and store them for the redo command
        self.deleted_edges = self.schematic.delete_node(node_name)
        self.logger.debug(f"Deleted node with config: {node_name}")
        self.logger.debug(f"Deleted edges: {self.deleted_edges}")

        # status message
        edges_count = len(self.deleted_edges)
        status_message = f"Deleted node '{node_name}'"
        if edges_count == 1:
            status_message += " and its edge"
        elif edges_count > 1:
            status_message += f" and its {edges_count} edges"

        self.schematic.app.status_message.emit(status_message)

        # update widgets
        self.schematic.app.components_tree.reload()
        self.schematic.reload()
