from typing import TYPE_CHECKING

from pywr_editor.style import Color

from .circle import Circle

if TYPE_CHECKING:
    from pywr_editor.schematic import SchematicNode


class BlueCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
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
    def __init__(self, parent: "SchematicNode"):
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
    def __init__(self, parent: "SchematicNode"):
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
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for an orange circle.
        """
        super().__init__(
            parent=parent, fill=Color("amber", 200), outline=Color("amber", 600)
        )


class RedCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for an red circle.
        """
        super().__init__(
            parent=parent, fill=Color("red", 200), outline=Color("red", 600)
        )


class PurpleCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for an purple circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("purple", 200),
            outline=Color("purple", 600),
        )


class PinkCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for an pink circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("pink", 200),
            outline=Color("pink", 600),
        )
