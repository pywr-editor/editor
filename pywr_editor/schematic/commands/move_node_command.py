from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from pywr_editor.schematic import Schematic, SchematicNode


class MoveNodeCommand(QUndoCommand):
    def __init__(
        self, schematic: "Schematic", selected_nodes: list["SchematicNode"]
    ):
        """
        Initialises the delete node command.
        :param schematic: The Schematic instance.
        :return: None
        """
        super().__init__()

        self.logger = Logging().logger(self.__class__.__name__)
        self.schematic = schematic
        self.node_configs = [
            self.schematic.model_config.nodes.get_node_config_from_name(
                node.name, as_dict=False
            )
            for node in selected_nodes
        ]
        self.prev_positions: list[tuple[float, float]] = []
        self.updated_positions: list[tuple[float, float]] = []

        total_nodes = len(selected_nodes)
        suffix = "node" if total_nodes == 1 else "nodes"
        self.setText(f"moved {total_nodes} {suffix}")

    def redo(self) -> None:
        """
        Saves the position of the moved nodes.
        :return: None
        """
        # nodes are moved for the first time
        if not self.updated_positions:
            for config in self.node_configs:
                item = self.schematic.node_items[config.name]
                self.prev_positions.append(item.prev_position)

                # prevent the nodes from being moved outside the schematic edges.
                item.adjust_node_position()
                # store the new positions of any selected nodes as long as the
                # nodes were moved
                item.save_position_if_moved()
                self.updated_positions.append(item.position)
            self.logger.debug(f"Moved {len(self.node_configs)} nodes")
        # redo position after undo
        else:
            for node_config, position in zip(
                self.node_configs, self.updated_positions
            ):
                self.schematic.app.model_config.nodes.set_position(
                    node_name=node_config.name, position=position
                )
                self.logger.debug(f"Removed {node_config.name} to {position}")
            self.schematic.reload()

    def undo(self) -> None:
        """
        Restores the previous position.
        :return: None
        """
        for node_config, prev_position in zip(
            self.node_configs, self.prev_positions
        ):
            self.schematic.app.model_config.nodes.set_position(
                node_name=node_config.name, position=prev_position
            )
            self.logger.debug(f"Restored {node_config.name} to {prev_position}")
        self.schematic.reload()
