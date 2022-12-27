from typing import TYPE_CHECKING

from pywr_editor.model import BaseShape as ModelBaseShape

if TYPE_CHECKING:
    from pywr_editor.schematic import Schematic


class BaseShape:
    """
    Abstract class each shape inherits from. This is used
    to identify which graphical item is a shape on the schematic.
    """

    def __init__(self, shape_id: str, shape: ModelBaseShape, view: "Schematic"):
        """
        Initialise the text shape.
        :param shape_id: The shape ID.
        :param shape: The instance with the shape configuration inheriting from
        ModelBaseShape.
        :param view: The view where to draw the item.
        """
        self.id = shape_id
        self.view = view
        self.shape_obj = shape
