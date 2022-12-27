import pytest
from PySide6.QtGui import QColor

from pywr_editor.model import ModelConfig, Shapes
from pywr_editor.model.shapes import BaseShape, TextShape
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
                    "y": 1.2,
                },
                False,
            ),
            # missing y
            (
                {
                    "x": 1.2,
                },
                False,
            ),
            # wrong x
            (
                {
                    "x": "a",
                },
                False,
            ),
            # valid
            (
                {
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
        assert (
            BaseShape(id="shape", shape_dict=shape_dict, type="text").is_valid()
            == is_valid
        )

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
                {"x": 100, "y": 200, "font_size": [120]},
                False,
            ),
            # font size outside bounds
            (
                {"x": 100, "y": 200, "font_size": 120},
                False,
            ),
            # missing text
            (
                {
                    "x": 100,
                    "y": 200,
                },
                False,
            ),
            # text too short
            (
                {"x": 100, "y": 200, "text": "A"},
                False,
            ),
            # valid
            (
                {
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
        Tests the TextShape validation
        """
        assert (
            TextShape(id="shape", shape_dict=shape_dict, type="text").is_valid()
            == is_valid
        )