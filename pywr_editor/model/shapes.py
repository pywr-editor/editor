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
            self.x = self.shape_dict.get("x", None)
            self.y = self.shape_dict.get("y", None)

    def is_valid(self) -> bool:
        """
        Checks the shape configuration dictionary.
        :return: Whether the shape configuration is valid.
        """
        return (
            isinstance(self.shape_dict, dict)
            and "id" in self.shape_dict
            and "x" in self.shape_dict
            and "y" in self.shape_dict
            and isinstance(self.shape_dict["id"], str)
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

        if rgb is not None and isinstance(rgb, (list, tuple)) and len(rgb) == 3:
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

    shape_type: str = "text"
    """ The type of the shape """
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

    @staticmethod
    def create(shape_id: str, position: Sequence[float]) -> "TextShape":
        """
        Creates a new dictionary with the shape properties.
        :param shape_id: The shape iD.
        :param position: The node position.
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
class Shapes:
    model: "ModelConfig"
    """ The ModelConfig instance """

    def __post_init__(self):
        self.shape_type_map = {TextShape.shape_type: TextShape}

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
        position: list[float],
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
