from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

from pywr_editor.model import RectangleShape
from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from pywr_editor.schematic import Schematic, SchematicRectangle


class ResizeShapeCommand(QUndoCommand):
    """
    Undo command used to undo/redo size change of a shape.
    """

    def __init__(
        self,
        schematic: "Schematic",
        selected_shape: "SchematicRectangle",
    ):
        """
        Initialise the command.
        :param schematic: The Schematic instance.
        :param selected_shape: The selected schematic shape instance being resized.
        :return: None
        """
        super().__init__()

        self.logger = Logging().logger(self.__class__.__name__)
        self.schematic = schematic
        self.model_config = schematic.model_config
        self.resized_shape_id = selected_shape.id

        self.prev_size: tuple[float, float] | None = None
        self.prev_pos: tuple[float, float] | None = None
        self.updated_size: tuple[float, float] | None = None
        self.updated_pos: tuple[float, float] | None = None

        self.setText("resized 1 shape")

    def redo(self) -> None:
        """
        Resizes the shape.
        :return: None
        """
        # the shape is resized for the first time
        if not self.updated_size:
            # store the previous position and size
            shape_config: RectangleShape = self.model_config.shapes.find_shape(
                shape_id=self.resized_shape_id
            )
            self.prev_size = tuple([shape_config.width, shape_config.height])
            self.prev_pos = tuple([shape_config.x, shape_config.y])

            # update the new position and size
            shape_item = self.schematic.shape_items[self.resized_shape_id]
            rect = shape_item.rect()
            self.updated_size = tuple(
                map(lambda x: round(x, 5), rect.size().toTuple())
            )

            # convert to absolute coordinates
            self.updated_pos = shape_item.mapToScene(
                round(rect.x(), 5), round(rect.y(), 5)
            ).toTuple()

            # delete command if the shape has not changed size or position
            if (
                self.prev_pos == self.updated_pos
                and self.prev_size == self.updated_size
            ):
                self.setObsolete(True)
                return

            self.model_config.shapes.set_size(
                shape_id=self.resized_shape_id, size=self.updated_size
            )
            self.model_config.shapes.set_position(
                shape_id=self.resized_shape_id, position=self.updated_pos
            )
            self.logger.debug(f"Resized shape '{self.resized_shape_id}'")
        # redo position after undo
        else:
            self.model_config.shapes.set_size(
                shape_id=self.resized_shape_id, size=self.updated_size
            )
            self.model_config.shapes.set_position(
                shape_id=self.resized_shape_id,
                position=self.updated_pos,
            )
            self.logger.debug(
                f"Changed size from {self.prev_size}' to {self.updated_size} "
                + f"and position from {self.prev_pos} to {self.updated_pos} "
                + f"for shape '{self.resized_shape_id}'"
            )
            self.schematic.reload()

    def undo(self) -> None:
        """
        Restores the previous position.
        :return: None
        """
        self.model_config.shapes.set_size(
            shape_id=self.resized_shape_id, size=self.prev_size
        )
        self.model_config.shapes.set_position(
            shape_id=self.resized_shape_id, position=self.prev_pos
        )
        self.logger.debug(
            f"Restore size from {self.updated_size}' to {self.prev_size} "
            + f"and position from {self.updated_pos} to {self.prev_pos} "
            + f"for shape '{self.resized_shape_id}'"
        )

        self.schematic.reload()
