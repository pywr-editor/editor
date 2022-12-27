import numpy as np
import pytest
from PySide6.QtCore import QTimer

from pywr_editor.main_window import MainWindow
from tests.utils import close_message_box, resolve_model_path


class TestSchematicCoordinatesTransformation:
    model_file = resolve_model_path("test_coordinates.json")

    @pytest.fixture
    def window(self) -> MainWindow:
        """
        Initialise the window.
        :return: The MainWindow instance.
        """
        QTimer.singleShot(200, close_message_box)
        win = MainWindow(self.model_file)
        win.hide()
        return win

    @staticmethod
    def np_to_px(
        point: list[float], pywr_bounds: list[float], px_bounds: list[float]
    ) -> list[float]:
        """
        Transform the coordinates using numpy.interp.
        :param point: The point to transform.
        :param pywr_bounds: The pywr bounds.
        :param px_bounds: The schematic pounds.
        :return: The converted coordinates.
        """
        return [
            round(np.interp(point[0], pywr_bounds, (0, px_bounds[0])), 4),
            round(np.interp(-point[1], pywr_bounds, (0, px_bounds[1])), 4),
        ]

    def test_coordinate_transformation(self, qtbot, window):
        """
        Test the coordinate transformation from the Pywr system coordinates to the
        pixel system coordinates. Do not use np.interp in the editor, to avoid
        including numpy as dependency.
        """
        schematic = window.schematic
        schematic_size = [schematic.schematic_width, schematic.schematic_height]
        for node in window.model_config.json["nodes"]:
            point_pywr = node["position"]["schematic"]
            assert schematic.to_px(point_pywr) == self.np_to_px(
                point_pywr, schematic.pywr_bounds, schematic_size
            )
