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


class StoneCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for a stone circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("stone", 200),
            outline=Color("stone", 600),
            label=Color("stone", 700),
        )


class AmberCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for a amber circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("amber", 200),
            outline=Color("amber", 600),
            label=Color("amber", 700),
        )


class YellowCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for a yellow circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("yellow", 200),
            outline=Color("yellow", 600),
            label=Color("yellow", 700),
        )


class LimeCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for a lime circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("lime", 200),
            outline=Color("lime", 600),
            label=Color("lime", 700),
        )


class EmeraldCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for a emerald circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("emerald", 200),
            outline=Color("emerald", 600),
            label=Color("emerald", 700),
        )


class TealCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for a teal circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("teal", 200),
            outline=Color("teal", 600),
            label=Color("teal", 700),
        )


class CyanCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for a cyan circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("cyan", 200),
            outline=Color("cyan", 600),
            label=Color("cyan", 700),
        )


class SkyCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for a sky circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("sky", 200),
            outline=Color("sky", 600),
            label=Color("sky", 700),
        )


class IndigoCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for a indigo circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("indigo", 200),
            outline=Color("indigo", 600),
            label=Color("indigo", 700),
        )


class VioletCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for a violet circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("violet", 200),
            outline=Color("violet", 600),
            label=Color("violet", 700),
        )


class FuchsiaCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for a fuchsia circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("fuchsia", 200),
            outline=Color("fuchsia", 600),
            label=Color("fuchsia", 700),
        )


class RoseCircle(Circle):
    def __init__(self, parent: "SchematicNode"):
        """
        Initialises the shape for a rose circle.
        """
        super().__init__(
            parent=parent,
            fill=Color("rose", 300),
            outline=Color("rose", 700),
            label=Color("rose", 700),
        )
