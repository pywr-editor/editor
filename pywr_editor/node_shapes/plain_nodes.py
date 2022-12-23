from typing import TYPE_CHECKING

from pywr_editor.style import Color

from .circle import Circle

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicItem


class BlueCircle(Circle):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the shape for a blue circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("blue", 200),
            outline=Color("blue", 600),
            label=Color("blue", 700),
        )


class GrayCircle(Circle):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the shape for a gray circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("gray", 200),
            outline=Color("gray", 600),
            label=Color("gray", 700),
        )


class GreenCircle(Circle):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the shape for a blue circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("green", 200),
            outline=Color("green", 600),
            label=Color("green", 700),
        )


class OrangeCircle(Circle):
    def __init__(self, parent: "SchematicItem"):
        """
        Initialises the shape for an orange circle.
        """
        super().__init__(
            parent=parent, fill=Color("amber", 200), outline=Color("amber", 600)
        )
