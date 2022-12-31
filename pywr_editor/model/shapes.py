from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from PySide6.QtGui import QColor

from pywr_editor.model import Constants
from pywr_editor.style import Color

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig


@dataclass
class BaseShape:
    shape_dict: dict
    """ The shape dictionary with the ID, x and y keys. """

    def __post_init__(self):
        """
        Define the shape properties.
        :return: None
        """
        if isinstance(self.shape_dict, dict):
            self.id = self.shape_dict.get("id", None)

    @property
    def type(self) -> str:
        """
        Returns a string identifying the shape type.
        :return: The shape type.
        """
        return self.shape_dict["type"]

    @property
    def x(self) -> float:
        """
        Returns the shape's x coordinate.
        :return: The x coordinate.
        """
        return self.shape_dict["x"]

    @property
    def y(self) -> float:
        """
        Returns the shape's y coordinate.
        :return: The y coordinate.
        """
        return self.shape_dict["y"]

    def is_valid(self) -> bool:
        """
        Checks the shape configuration dictionary.
        :return: Whether the shape configuration is valid.
        """
        return (
            isinstance(self.shape_dict, dict)
            and "id" in self.shape_dict
            and "type" in self.shape_dict
            and "x" in self.shape_dict
            and "y" in self.shape_dict
            and isinstance(self.shape_dict["id"], str)
            and isinstance(self.shape_dict["type"], str)
            and isinstance(self.shape_dict["x"], (float, int))
            and isinstance(self.shape_dict["y"], (float, int))
        )

    @staticmethod
    def parse_color(
        rgb: Sequence[int] | None,
        default_rgb: Sequence[int] | None = tuple([0, 0, 0]),
    ) -> QColor:
        """
        Parses the RGB colour.
        :param rgb: The RGB colour.
        :param default_rgb: The RGB colour to use if the provided colour is not valid.
        :return: The QColor instance.
        """
        default_qcolor = QColor.fromRgb(*default_rgb)

        if (
            rgb is not None
            and isinstance(rgb, (list, tuple))
            and 3 <= len(rgb) <= 4
        ):
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
     - text: the text to write in the shape.
     - font_size: the font size in px. Optional.
     - color: A list of RGB values for the font colour. Optional
    """

    shape_type: str = "text"
    """ The type of the shape """
    default_font_size: int = 14
    """ The font size to use when it is not provided """
    default_font_color: tuple[int, int, int] = Color(name="gray", shade=800).rgb
    """ The default font colour to use when it is not provided """
    min_font_size: int = 10
    """ The minimum allowed font size """
    max_font_size: int = 50
    """ The maximum allowed font size """
    min_text_size: int = 3
    """ The text must have at least 3 characters """

    @property
    def text(self) -> str:
        """
        Returns the text.
        :return: The text.
        """
        return self.shape_dict["text"]

    @property
    def font_size(self) -> int:
        """
        Returns the font size.
        :return: The font size.
        """
        return self.shape_dict.get("font_size", self.default_font_size)

    @property
    def color(self) -> QColor:
        """
        Returns the text's colour.
        :return: The color instance.
        """
        return self.parse_color(
            self.shape_dict.get("color", None), self.default_font_color
        )

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

    @staticmethod
    def create(shape_id: str, position: Sequence[float]) -> "TextShape":
        """
        Creates a new dictionary with the shape properties.
        :param shape_id: The shape iD.
        :param position: The shape position.
        :return: The TextShape instance.
        """
        return TextShape(
            shape_dict={
                "id": shape_id,
                "text": "Label",
                "type": TextShape.shape_type,
                "x": position[0],
                "y": position[1],
            },
        )


@dataclass
class RectangleShape(BaseShape):
    """
    Define a rectangle. Available keys for shape_dict are:
     - width: the rectangle width.
     - height: the rectangle height.
     - border_size: the border size.
     - border_color: A list of RGB values for the border color. Optional
    """

    shape_type: str = "rectangle"
    """ The type of the shape """
    default_border_size: int = 1
    """ The border size to use when it is not provided """
    default_border_color: tuple[int, int, int] = Color(
        name="gray", shade=800
    ).rgb
    """ The default border colour to use when it is not provided """
    max_border_size: int = 5
    """ The maximum allowed border size """
    default_background_color = tuple([255, 255, 255, 255])
    """ The default background colour """

    @property
    def width(self) -> float:
        """
        Returns the rectangle's width.
        :return: The width.
        """
        return self.shape_dict.get("width")

    @property
    def height(self) -> float:
        """
        Returns the rectangle's height.
        :return: The height.
        """
        return self.shape_dict.get("height")

    @property
    def border_color(self) -> QColor:
        """
        Returns the border colour.
        :return: The colour instance.
        """
        return self.parse_color(
            self.shape_dict.get("border_color", None), self.default_border_color
        )

    @property
    def border_size(self) -> int:
        """
        Returns the border size.
        :return: The colour as RGB values.
        """
        return self.shape_dict.get("border_size", self.default_border_size)

    @property
    def background_color(self) -> QColor:
        """
        Returns the background colour.
        :return: The colour instance.
        """
        return self.parse_color(
            self.shape_dict.get("background_color", None),
            self.default_background_color,
        )

    def is_valid(self) -> bool:
        """
        Validates the shape configuration dictionary.
        :return: Whether the configuration is valid.
        """
        return super().is_valid() and (
            isinstance(self.width, (int, float))
            and isinstance(self.height, (int, float))
            and isinstance(self.border_size, int)
            and 1 <= self.border_size <= self.max_border_size
        )

    @staticmethod
    def create(
        shape_id: str, position: Sequence[float], size: Sequence[float]
    ) -> "RectangleShape":
        """
        Creates a new dictionary with the shape properties.
        :param shape_id: The shape iD.
        :param position: The rectangle position.
        :param size: The rectangle size.
        :return: The RectangleShape instance.
        """
        return RectangleShape(
            shape_dict={
                "id": shape_id,
                "type": RectangleShape.shape_type,
                "width": size[0],
                "height": size[1],
                "x": position[0],
                "y": position[1],
            },
        )


@dataclass
class Shapes:
    model: "ModelConfig"
    """ The ModelConfig instance """

    def __post_init__(self):
        self.shape_type_map = {
            TextShape.shape_type: TextShape,
            RectangleShape.shape_type: RectangleShape,
        }

    def get_all(self) -> list[BaseShape]:
        """
        Returns the list of shapes.
        :return: A list of shape instances.
        """
        if (
            Constants.SHAPES_KEY.value not in self.model.editor_config
            or not isinstance(
                self.model.editor_config[Constants.SHAPES_KEY.value], list
            )
        ):
            return []

        shapes = []
        for shape_dict in self.model.editor_config[Constants.SHAPES_KEY.value]:
            try:
                shape_class_type = self.shape_type_map[shape_dict.get("type")]
                shape: BaseShape = shape_class_type(shape_dict=shape_dict)
                if shape.is_valid():
                    shapes.append(shape)
            # ignore invalid configurations
            except (TypeError, KeyError):
                continue

        return shapes

    def find_shape_index_by_id(self, shape_id: str) -> int | None:
        """
        Finds the shape index in the list by the shape ID.
        :param shape_id: The shape ID to look for.
        :return: The shape index if the ID is found. None otherwise.
        """
        return next(
            (
                idx
                for idx, shape_dict in enumerate(
                    self.model.editor_config[Constants.SHAPES_KEY.value]
                )
                if shape_dict["id"] == shape_id
            ),
            None,
        )

    def find_shape(
        self, shape_id: str, as_dict=False
    ) -> dict | BaseShape | None:
        """
        Find the shape by ID and get its dictionary.
        :param shape_id: The shape ID.
        :param as_dict: Whether to return the shape configuration dictionary or
        the shape instance. Default to False.
        :return: The shape dictionary if the ID is found, None otherwise.
        """
        idx = self.find_shape_index_by_id(shape_id)
        if idx is not None:
            shape_dict = self.model.editor_config[Constants.SHAPES_KEY.value][
                idx
            ]
            # return dictionary
            if as_dict:
                return shape_dict

            try:
                shape_class_type = self.shape_type_map[shape_dict.get("type")]
                shape: BaseShape = shape_class_type(shape_dict=shape_dict)
                if shape.is_valid():
                    return shape
            # ignore invalid configurations
            except (TypeError, KeyError):
                return None

    def delete(self, shape_id: str) -> None:
        """
        Delete the shape by ID.
        :param shape_id: The shape ID.
        :return: None.
        """
        idx = self.find_shape_index_by_id(shape_id)
        if idx is None:
            return

        del self.model.editor_config[Constants.SHAPES_KEY.value][idx]
        self.model.changes_tracker.add(f"Deleted shape {shape_id}")

    def update(self, shape_id: str, shape_dict: dict) -> None:
        """
        Add or save an existing shape shape.
        :param shape_id: The shape ID to update or add.
        :param shape_dict: The shape dictionary.
        :return: None
        """
        idx = self.find_shape_index_by_id(shape_id)
        # add shape for the first time
        if idx is None:
            self.model.editor_config[Constants.SHAPES_KEY.value].append(
                shape_dict
            )
            action = "Added"
        # update existing shape dictionary
        else:
            self.model.editor_config[Constants.SHAPES_KEY.value][
                idx
            ] = shape_dict
            action = "Updated"

        self.model.changes_tracker.add(
            f"{action} shape {shape_id} with the following values: {shape_dict}"
        )

    def set_position(
        self,
        position: list[float, int],
        shape_id: str,
    ) -> None:
        """
        Sets or updates the position of a shape.
        :param position: The position to set as list.
        :param shape_id: The shape ID.
        :return None
        """
        idx = self.find_shape_index_by_id(shape_id)
        if idx is None:
            return

        shape_dict = self.model.editor_config[Constants.SHAPES_KEY.value][idx]
        shape_dict["x"] = position[0]
        shape_dict["y"] = position[1]

        self.model.changes_tracker.add(
            f'Changed position for shape "{shape_id}" to {position}'
        )

    def set_size(
        self,
        size: list[float, int],
        shape_id: str,
    ) -> None:
        """
        Sets or updates the size of a shape. Note that some shapes do not have a size.
        :param size: The shape width and height.
        :param shape_id: The shape ID.
        :return None
        """
        idx = self.find_shape_index_by_id(shape_id)
        if idx is None:
            return

        shape_dict = self.model.editor_config[Constants.SHAPES_KEY.value][idx]
        if "width" not in shape_dict or "height" not in shape_dict:
            return
        shape_dict["width"] = size[0]
        shape_dict["height"] = size[1]

        self.model.changes_tracker.add(
            f'Changed size for shape "{shape_id}" to {size}'
        )
