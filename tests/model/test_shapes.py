import pytest
from PySide6.QtGui import QColor

from pywr_editor.model import (
    BaseShape,
    LineArrowShape,
    ModelConfig,
    RectangleShape,
    Shapes,
    TextShape,
)
from tests.utils import resolve_model_path


class TestShapes:
    @staticmethod
    def shapes() -> Shapes:
        """
        Initialises the Shapes class.
        :return: The Edges instance.
        """
        return Shapes(ModelConfig(resolve_model_path("model_1.json")))

    @pytest.mark.parametrize(
        "shape_dict, is_valid",
        [
            # empty dict
            ({}, False),
            # invalid type
            ([], False),
            # missing x
            (
                {
                    "id": "aaa",
                    "type": "shape",
                    "y": 1.2,
                },
                False,
            ),
            # missing y
            (
                {
                    "id": "aaa",
                    "type": "shape",
                    "x": 1.2,
                },
                False,
            ),
            # wrong x
            (
                {
                    "id": "aaa",
                    "type": "shape",
                    "x": "a",
                    "y": 100,
                },
                False,
            ),
            # valid
            (
                {
                    "id": "aaa",
                    "type": "shape",
                    "x": 100,
                    "y": 200,
                },
                True,
            ),
        ],
    )
    def test_base_shape(self, shape_dict, is_valid):
        """
        Tests the BaseShape validation
        """
        assert BaseShape(shape_dict=shape_dict).is_valid() == is_valid

    @pytest.mark.parametrize(
        "rgb, default_rgb, expected",
        [
            # no colour or default
            (None, None, QColor(0, 0, 0)),
            # no colour, different default value
            (None, [120, 120, 120], QColor(120, 120, 120)),
            # colour provided
            ([45, 45, 45], None, QColor(45, 45, 45)),
            # wrong colour provided
            ([450, 450, 450], None, QColor(0, 0, 0)),
        ],
    )
    def test_parse_color(self, rgb, default_rgb, expected):
        """
        Tests the parse_color method
        """
        if default_rgb:
            assert BaseShape.parse_color(rgb, default_rgb) == expected
        else:
            assert BaseShape.parse_color(rgb) == expected

    @pytest.mark.parametrize(
        "shape_dict, is_valid",
        [
            # wrong font size type
            (
                {"id": "aaa", "x": 100, "y": 200, "font_size": [120]},
                False,
            ),
            # font size outside bounds
            (
                {
                    "id": "aaa",
                    "type": "text",
                    "x": 100,
                    "y": 200,
                    "font_size": 120,
                },
                False,
            ),
            # missing text
            (
                {
                    "id": "aaa",
                    "type": "text",
                    "x": 100,
                    "y": 200,
                },
                False,
            ),
            # text too short
            (
                {"id": "aaa", "type": "text", "x": 100, "y": 200, "text": "A"},
                False,
            ),
            # valid
            (
                {
                    "id": "aaa",
                    "type": "text",
                    "x": 100,
                    "y": 200,
                    "text": "Example",
                    "font_size": 15,
                },
                True,
            ),
        ],
    )
    def test_text_shape(self, shape_dict, is_valid):
        """
        Test the TextShape validation
        """
        assert TextShape(shape_dict=shape_dict).is_valid() == is_valid

    @pytest.mark.parametrize(
        "shape_dict, is_valid",
        [
            # missing width
            (
                {
                    "id": "aaa",
                    "type": "rectangle",
                    "x": 100,
                    "y": 200,
                    "height": 120,
                },
                False,
            ),
            # missing height
            (
                {
                    "id": "aaa",
                    "type": "rectangle",
                    "x": 100,
                    "y": 200,
                    "width": 120,
                },
                False,
            ),
            # wrong size type
            (
                {
                    "id": "aaa",
                    "type": "rectangle",
                    "x": 100,
                    "y": 200,
                    "width": 120,
                    "height": "100",
                },
                False,
            ),
            # wrong border size type
            (
                {
                    "id": "aaa",
                    "type": "rectangle",
                    "x": 100,
                    "y": 200,
                    "width": 120,
                    "height": "100",
                    "border_size": 1.6,
                },
                False,
            ),
            # border size too large
            (
                {
                    "id": "aaa",
                    "type": "rectangle",
                    "x": 100,
                    "y": 200,
                    "width": 120,
                    "height": 100,
                    "border_size": 100,
                },
                False,
            ),
            # valid
            (
                {
                    "id": "aaa",
                    "type": "rectangle",
                    "x": 100,
                    "y": 200,
                    "width": 120,
                    "height": 100,
                    "border_size": 2,
                },
                True,
            ),
        ],
    )
    def test_rectangle_shape(self, shape_dict, is_valid):
        """
        Test the RectangleShape validation.
        """
        assert RectangleShape(shape_dict=shape_dict).is_valid() == is_valid

    @pytest.mark.parametrize(
        "shape_dict, is_valid",
        [
            # missing length
            (
                {
                    "id": "aaa",
                    "type": "arrow",
                    "x": 100,
                    "y": 200,
                    "angle": 120,
                },
                False,
            ),
            # missing angle
            (
                {
                    "id": "aaa",
                    "type": "arrow",
                    "x": 100,
                    "y": 200,
                    "length": 120,
                },
                False,
            ),
            # wrong lengths
            (
                {
                    "id": "aaa",
                    "type": "arrow",
                    "x": 100,
                    "y": 200,
                    "angle": 120,
                    "length": "100",
                },
                False,
            ),
            (
                {
                    "id": "aaa",
                    "type": "arrow",
                    "x": 100,
                    "y": 200,
                    "angle": 120,
                    "length": -100,
                },
                False,
            ),
            # wrong border size type
            (
                {
                    "id": "aaa",
                    "type": "arrow",
                    "x": 100,
                    "y": 200,
                    "angle": 120,
                    "length": 100,
                    "border_size": 1.6,
                },
                False,
            ),
            # border size too large
            (
                {
                    "id": "aaa",
                    "type": "arrow",
                    "x": 100,
                    "y": 200,
                    "angle": 120,
                    "length": 100,
                    "border_size": 100,
                },
                False,
            ),
            # valid
            (
                {
                    "id": "aaa",
                    "type": "arrow",
                    "x": 100,
                    "y": 200,
                    "angle": 120,
                    "length": 100,
                    "border_size": 2,
                },
                True,
            ),
        ],
    )
    def test_arrow_shape(self, shape_dict, is_valid):
        """
        Test the LineArrowShape validation.
        """
        assert LineArrowShape(shape_dict=shape_dict).is_valid() == is_valid
