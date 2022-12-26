from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Sequence

from PySide6.QtGui import QColor

from pywr_editor.style import Color

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig


@dataclass
class BaseShape:
    id: str
    """ The ID of the shape """
    type: Literal["text"]
    """ The shape type. Valid types are: 'text' """
    shape_dict: dict
    """ The shape dictionary with the x and y key for the shape coordinates """

    def __post_init__(self):
        """
        Defines the shape properties.
        :return: None
        """
        if isinstance(self.shape_dict, dict):
            self.x = self.shape_dict.get("x", None)
            self.y = self.shape_dict.get("y", None)

    def is_valid(self) -> bool:
        """
        Checks the shape configuration dictionary.
        :return: Whether the shape configuration is valid.
        """
        return (
            isinstance(self.shape_dict, dict)
            and "x" in self.shape_dict
            and "y" in self.shape_dict
            and isinstance(self.shape_dict["x"], (float, int))
            and isinstance(self.shape_dict["y"], (float, int))
        )

    @staticmethod
    def parse_color(
        rgb: Sequence[int] | None,
        default_rb: Sequence[int] | None = tuple([0, 0, 0]),
    ) -> QColor:
        """
        Parses the RGB colour.
        :param rgb: The RGB colour.
        :param default_rb: The RGB colour to use if the provided colour is not valid.
        :return: The QColor instance.
        """
        default_qcolor = QColor.fromRgb(*default_rb)

        if rgb is not None and isinstance(rgb, list) and len(rgb) == 3:
            qcolor = QColor.fromRgb(*rgb)
            # if RGB color is not valid use default
            if not qcolor.isValid():
                qcolor = default_qcolor
            return qcolor
        else:
            return default_qcolor


@dataclass
class TextShape(BaseShape):
    """
    Define a text shape. Available keys for shape_dict are:
     - text: The text to write in the shape.
     - font_size: The font size in px. Optional.
     - color: A list for the RGB font color. Optional
    """

    default_font_size: int = 14
    """ The font size to use when it is not provided """
    default_font_color: tuple[int] = Color(name="gray", shade=800).rgb
    """ The default font colour to use when it is not provided """
    min_font_size: int = 10
    """ The minimum allowed font size """
    max_font_size: int = 50
    """ The maximum allowed font size """
    min_text_size: int = 3
    """ The text must have at least 3 characters """

    def __post_init__(self):
        """
        Initialises the shape.
        """
        super().__post_init__()

        self.color = self.parse_color(
            self.shape_dict.get("color", None), self.default_font_color
        )
        self.text = self.shape_dict.get("text")
        self.font_size = self.shape_dict.get(
            "font_size", self.default_font_size
        )
        self.text = self.shape_dict.get("text")

    def is_valid(self) -> bool:
        """
        Validates the shape configuration dictionary.
        :return: Whether the configuration is valid.
        """
        return super().is_valid() and (
            isinstance(self.font_size, int)
            and (self.min_font_size <= self.font_size <= self.max_font_size)
            and isinstance(self.text, str)
            and len(self.text) >= self.min_text_size
        )


@dataclass
class Shapes:
    model: "ModelConfig"
    """ The ModelConfig instance """

    def __post_init__(self):
        self.shape_type_map = {"text": TextShape}

    def get_all(self) -> list[TextShape]:
        """
        Returns the list of edges.
        :return: The shape dictionary with the shape IDs as keys and the shape
        configurations as values.
        """
        if "shapes" not in self.model.editor_config or not isinstance(
            self.model.editor_config["shapes"], dict
        ):
            return []

        shapes = []
        for shape_id, shape_dict in self.model.editor_config["shapes"].items():
            if isinstance(shape_dict, dict) and "type" in shape_dict:
                try:
                    shape_class_type = self.shape_type_map[
                        shape_dict.get("type")
                    ]
                    shape: TextShape = shape_class_type(
                        id=shape_id,
                        shape_dict=shape_dict,
                        type=shape_dict.get("type"),
                    )
                    if shape.is_valid():
                        shapes.append(shape)
                # ignore invalid configurations
                except (TypeError, KeyError):
                    continue

        return shapes

    def update(self, shape_id: str, shape_dict: dict) -> None:
        """
        Saves the shape.
        :param shape_id: The shape ID to update.
        :param shape_dict: The shape dictionary.
        :return: None
        """
        if shape_id in self.model.editor_config["shapes"]:
            self.model.editor_config["shapes"][shape_id] = shape_dict
            self.model.changes_tracker.add(
                f"Updated shape {shape_id} with the following values: {shape_dict}"
            )
