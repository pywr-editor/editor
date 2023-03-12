from typing import TYPE_CHECKING, Union

from PySide6.QtGui import QUndoCommand

from pywr_editor.model import LineArrowShape, RectangleShape
from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from pywr_editor.schematic import (
        Schematic,
        SchematicArrow,
        SchematicRectangle,
    )


class ResizeShapeCommand(QUndoCommand):
    """
    Undo command used to undo/redo size change of a shape. This command
    supports the following shapes: rectangle and line arrow.
    """

    def __init__(
        self,
        schematic: "Schematic",
        selected_shape: Union["SchematicRectangle", "SchematicArrow"],
    ):
        """
        Initialise the command.
        :param schematic: The Schematic instance.
        :param selected_shape: The schematic shape instance being resized.
        :return: None
        """
        super().__init__()

        self.logger = Logging().logger(self.__class__.__name__)
        self.schematic = schematic
        self.selected_shape = selected_shape
        self.model_config = schematic.model_config
        self.resized_shape_id = selected_shape.id

        # other_info contains to the size for a rectangle or the target point
        # for a line
        self.prev_other_info: tuple[float, float] | dict | None = None
        self.prev_pos: tuple[float, float] | None = None
        self.updated_other_info: tuple[float, float] | dict | None = None
        self.updated_pos: tuple[float, float] | None = None

        self.setText("resized 1 shape")

    def redo(self) -> None:
        """
        Resizes the shape.
        :return: None
        """
        # the shape is resized for the first time
        if not self.updated_other_info:
            # store the previous position and size/target point
            shape_config: RectangleShape | LineArrowShape = (
                self.model_config.shapes.find_shape(
                    shape_id=self.resized_shape_id
                )
            )
            shape_item = self.schematic.shape_items[self.resized_shape_id]

            if self.is_rectangle:
                self.prev_other_info = tuple(
                    [shape_config.width, shape_config.height]
                )
                shape_native_obj = shape_item.rect()
                new_pos = [shape_native_obj.x(), shape_native_obj.y()]
            elif self.is_arrow:
                self.prev_other_info = dict(
                    angle=shape_config.angle, length=shape_config.length
                )
                shape_native_obj = shape_item.line()
                new_pos = [shape_native_obj.x1(), shape_native_obj.y1()]
            else:
                raise TypeError("The shape must be a rectangle or arrow")
            self.prev_pos = tuple([shape_config.x, shape_config.y])

            # update the new position and  size/target point

            if self.is_rectangle:
                self.updated_other_info = tuple(
                    map(
                        lambda x: round(x, 5), shape_native_obj.size().toTuple()
                    )
                )
            else:
                self.updated_other_info = dict(
                    angle=round(shape_native_obj.angle(), 3),
                    length=round(shape_native_obj.length(), 3),
                )

            # convert to absolute coordinates
            self.updated_pos = shape_item.mapToScene(
                round(new_pos[0], 5), round(new_pos[1], 5)
            ).toTuple()

            # delete command if the shape has not changed size or position
            if (
                self.prev_pos == self.updated_pos
                and self.prev_other_info == self.updated_other_info
            ):
                self.setObsolete(True)
                return

            # save new position
            self.model_config.shapes.set_position(
                shape_id=self.resized_shape_id, position=self.updated_pos
            )
            # save other information
            if self.is_rectangle:
                self.model_config.shapes.set_size(
                    shape_id=self.resized_shape_id, size=self.updated_other_info
                )
            else:
                self.model_config.shapes.set_line_data(
                    shape_id=self.resized_shape_id,
                    length=self.updated_other_info["length"],
                    angle=self.updated_other_info["angle"],
                )

            self.logger.debug(f"Resized shape '{self.resized_shape_id}'")
        # redo position after undo
        else:
            if self.is_rectangle:
                info_type = "size"
                self.model_config.shapes.set_size(
                    shape_id=self.resized_shape_id, size=self.updated_other_info
                )
            else:
                info_type = "angle and length"
                self.model_config.shapes.set_line_data(
                    shape_id=self.resized_shape_id,
                    length=self.updated_other_info["length"],
                    angle=self.updated_other_info["angle"],
                )

            self.model_config.shapes.set_position(
                shape_id=self.resized_shape_id,
                position=self.updated_pos,
            )
            self.logger.debug(
                f"Changed {info_type} from {self.prev_other_info}' to "
                f"{self.updated_other_info} and position from {self.prev_pos} "
                f"to {self.updated_pos} for shape '{self.resized_shape_id}'"
            )
            self.schematic.reload()

    def undo(self) -> None:
        """
        Restores the previous position and size.
        :return: None
        """
        if self.is_rectangle:
            info_type = "size"
            self.model_config.shapes.set_size(
                shape_id=self.resized_shape_id, size=self.prev_other_info
            )
        else:
            info_type = "angle and length"
            self.model_config.shapes.set_line_data(
                shape_id=self.resized_shape_id,
                length=self.prev_other_info["length"],
                angle=self.prev_other_info["angle"],
            )

        self.model_config.shapes.set_position(
            shape_id=self.resized_shape_id, position=self.prev_pos
        )

        self.logger.debug(
            f"Restore {info_type} from {self.updated_other_info}' to "
            f"{self.prev_other_info} and position from {self.updated_pos} to "
            f" {self.prev_pos} for shape '{self.resized_shape_id}'"
        )

        self.schematic.reload()

    @property
    def is_rectangle(self) -> bool:
        """
        Returns if the shape is a rectangle.
        :return: Whether the shape is a SchematicRectangle instance.
        """
        from pywr_editor.schematic import SchematicRectangle

        return isinstance(self.selected_shape, SchematicRectangle)

    @property
    def is_arrow(self) -> bool:
        """
        Returns if the shape is a line arrow.
        :return: Whether the shape is a SchematicArrow instance.
        """
        from pywr_editor.schematic import SchematicArrow

        return isinstance(self.selected_shape, SchematicArrow)
