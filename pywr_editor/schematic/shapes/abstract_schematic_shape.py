from typing import TYPE_CHECKING

from ..abstract_schematic_item import AbstractSchematicItem

if TYPE_CHECKING:
    from pywr_editor.model import BaseShape as ModelBaseShape
    from pywr_editor.schematic import Schematic


class AbstractSchematicShape(AbstractSchematicItem):
    """
    Abstract class each shape inherits from. This is used to identify which graphical
    item is a shape on the schematic and store basic shape properties.
    """

    def __init__(
        self, shape_id: str, shape: "ModelBaseShape", view: "Schematic"
    ):
        """
        Initialise the text shape.
        :param shape_id: The shape ID.
        :param shape: The instance with the shape configuration inheriting from
        ModelBaseShape.
        :param view: The view where to draw the item.
        """
        super().__init__(view)
        self.id = shape_id
        self.shape_obj = shape

    def save_position_if_moved(self) -> None:
        """
        Save the new shape position in the configuration file.
        :return: None
        """
        if self.has_position_changed():
            self.view.app.model_config.shapes.set_position(
                shape_id=self.id, position=self.position
            )
            self.prev_position = self.position
