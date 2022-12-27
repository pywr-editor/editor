from typing import Tuple

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLineEdit

from pywr_editor import MainWindow
from pywr_editor.form.widgets.color_picker_widget import ColorPickerWidget
from pywr_editor.schematic import Schematic
from pywr_editor.schematic.shapes.shape_dialogs import ShapeDialogForm
from tests.utils import close_message_box, resolve_model_path


class TestSchematicTextShape:
    model_file = resolve_model_path("model_1.json")

    @pytest.fixture
    def init_window(self) -> Tuple[MainWindow, Schematic]:
        """
        Initialise the window.
        :return: A tuple with the window and schematic instances.
        """
        QTimer.singleShot(100, close_message_box)
        window = MainWindow(self.model_file)
        window.hide()
        schematic = window.schematic

        return window, schematic

    def test_load_shape(self, qtbot, init_window):
        """
        Test that the text shape is properly load on the schematic.
        """
        window, schematic = init_window
        model_config = window.model_config
        shape_id = "c60bfe"
        shape_dict = {
            "text": "This is a label",
            "color": (255, 170, 0),
            "type": "text",
            "x": 410.1829,
            "y": 124.644,
        }

        assert shape_id in schematic.shape_items

        # 1. Check text properties
        item = schematic.shape_items[shape_id]
        assert item.toPlainText() == shape_dict["text"]
        assert item.pos().toTuple() == (shape_dict["x"], shape_dict["y"])
        assert item.defaultTextColor().toTuple()[0:3] == shape_dict["color"]

        # 2. Change text colour and label
        item.on_edit_shape()
        # noinspection PyTypeChecker
        form: ShapeDialogForm = window.findChild(ShapeDialogForm)

        text_field: QLineEdit = form.find_field_by_name("text").widget
        new_text = "New label"
        text_field.setText(new_text)
        color_widget: ColorPickerWidget = form.find_field_by_name(
            "color"
        ).widget
        color_widget.value = (120, 120, 120)

        # 3. Send form and check the model config and schematic item
        form.save()
        assert model_config.has_changes is True
        assert model_config.shapes.find_shape(shape_id) == {
            **shape_dict,
            **{
                "id": shape_id,
                "text": new_text,
                "color": color_widget.value,
            },
        }

        item = schematic.shape_items[shape_id]
        assert item.toPlainText() == new_text
        assert item.defaultTextColor().toTuple()[0:3] == color_widget.value
