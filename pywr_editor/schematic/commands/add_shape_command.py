from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from pywr_editor.model import BaseShape
    from pywr_editor.schematic import Schematic


class AddShapeCommand(QUndoCommand):
    def __init__(
        self,
        schematic: "Schematic",
        added_shape_obj: "BaseShape",
    ):
        """
        Initialises the add shape command.
        :param schematic: The Schematic instance.
        :param added_shape_obj: The shape instance to add.
        :return: None
        """
        super().__init__()

        self.logger = Logging().logger(self.__class__.__name__)
        self.schematic = schematic
        self.added_shape_config = added_shape_obj
        self.tracker_shape_config: BaseShape | None = None
        self.model_config = self.schematic.model_config
        self.setText("add new shape")

    def redo(self) -> None:
        """
        Adds the shape for the first time or restore it.
        :return: None
        """
        # add shape for the first time
        if self.tracker_shape_config is None:
            shape_config = self.added_shape_config
            status_message = "Added new shape"
        # restore shape node
        else:
            shape_config = self.tracker_shape_config
            status_message = "Restore shape"

        # add the shape to the schematic and model config
        self.model_config.shapes.update(
            shape_id=shape_config.id,
            shape_dict=shape_config.shape_dict,
        )
        self.schematic.add_shape(shape_obj=shape_config)

        self.logger.debug(
            f"{status_message} to schematic with: {shape_config.shape_dict}"
        )
        self.schematic.app.status_message.emit(status_message)

        # make sure shapes are inside the canvas
        self.schematic.adjust_items_initial_pos()

    def undo(self) -> None:
        """
        Removes the previously-added shape.
        :return: None
        """
        # store the latest configuration to be restored
        self.tracker_shape_config = self.model_config.shapes.find_shape(
            self.added_shape_config.id
        )

        self.schematic.delete_shape(self.added_shape_config.id)
        self.logger.debug(
            f"Deleted shape with config: {self.tracker_shape_config.shape_dict}"
        )
        self.schematic.app.status_message.emit("Deleted shape")

        # update schematic
        self.schematic.reload()
