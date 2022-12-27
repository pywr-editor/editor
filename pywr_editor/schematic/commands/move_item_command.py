from typing import TYPE_CHECKING, Union

from PySide6.QtGui import QUndoCommand

from pywr_editor.model import NodeConfig
from pywr_editor.utils import Logging

from ..node import SchematicNode
from ..shapes.abstract_schematic_shape import AbstractSchematicShape

if TYPE_CHECKING:
    from pywr_editor.schematic import AbstractSchematicItem, Schematic


class MoveItemCommand(QUndoCommand):
    """
    Undo command used to undo/redo position change of schematic items (nodes, edges
    and shapes).
    """

    def __init__(
        self,
        schematic: "Schematic",
        selected_items: list[Union["AbstractSchematicItem"]],
    ):
        """
        Initialise the command.
        :param schematic: The Schematic instance.
        :param selected_items: The list of selected schematic item instances to delete.
        :return: None
        """
        super().__init__()

        self.logger = Logging().logger(self.__class__.__name__)
        self.schematic = schematic
        self.model_config = schematic.model_config

        # list of nodes and shape configuration
        self.moved_item_configs = []
        for item in selected_items:
            if isinstance(item, SchematicNode):
                self.moved_item_configs.append(
                    self.model_config.nodes.get_node_config_from_name(
                        item.name, as_dict=False
                    )
                )
            elif isinstance(item, AbstractSchematicShape):
                self.moved_item_configs.append(
                    self.model_config.shapes.find_shape(item.id)
                )

        self.prev_positions: list[tuple[float, float]] = []
        self.updated_positions: list[tuple[float, float]] = []

        total_nodes = len(selected_items)
        suffix = "item" if total_nodes == 1 else "items"
        self.setText(f"moved {total_nodes} {suffix}")

    def redo(self) -> None:
        """
        Saves the position of the moved nodes.
        :return: None
        """
        # nodes are moved for the first time
        if not self.updated_positions:
            for config in self.moved_item_configs:
                if isinstance(config, NodeConfig):
                    item = self.schematic.node_items[config.name]
                else:
                    item = self.schematic.shape_items[config["id"]]

                self.prev_positions.append(item.prev_position)

                # prevent the items from being moved outside the schematic edges.
                item.adjust_position()
                # store the new positions of any selected nodes as long as the
                # items were moved
                item.save_position_if_moved()
                self.updated_positions.append(item.position)
            self.logger.debug(f"Moved {len(self.moved_item_configs)} items")
        # redo position after undo
        else:
            for item_config, position in zip(
                self.moved_item_configs, self.updated_positions
            ):
                if isinstance(item_config, NodeConfig):
                    self.model_config.nodes.set_position(
                        node_name=item_config.name, position=position
                    )
                    self.logger.debug(
                        f"Moved node '{item_config.name}' back to {position}"
                    )
                else:
                    self.model_config.shapes.set_position(
                        shape_id=item_config["id"], position=position
                    )
                    self.logger.debug(
                        f"Moved shape '{item_config['id']}' back to {position}"
                    )
            self.schematic.reload()

    def undo(self) -> None:
        """
        Restores the previous position.
        :return: None
        """
        for item_config, prev_position in zip(
            self.moved_item_configs, self.prev_positions
        ):
            if isinstance(item_config, NodeConfig):

                self.model_config.nodes.set_position(
                    node_name=item_config.name, position=prev_position
                )
                self.logger.debug(
                    f"Restored position '{item_config.name}' to {prev_position}"
                )
            else:
                self.model_config.shapes.set_position(
                    shape_id=item_config["id"], position=prev_position
                )
                self.logger.debug(
                    f"Restored position '{item_config['id']}' to {prev_position}"
                )

        self.schematic.reload()
