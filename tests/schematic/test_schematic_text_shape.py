from typing import Tuple

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLineEdit

from pywr_editor import MainWindow
from pywr_editor.form.widgets.color_picker_widget import ColorPickerWidget
from pywr_editor.model import BaseShape, ModelConfig, TextShape
from pywr_editor.schematic import Schematic
from pywr_editor.schematic.commands.delete_item_command import DeleteItemCommand
from pywr_editor.schematic.shapes.shape_dialogs import ShapeDialogForm
from pywr_editor.schematic.shapes.text_shape import SchematicText
from pywr_editor.widgets import SpinBox
from tests.utils import close_message_box, resolve_model_path


class TestSchematicTextShape:
    model_file = resolve_model_path("model_1.json")
    shape_id = "c60bfe"

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
        shape_config: TextShape = model_config.shapes.find_shape(self.shape_id)

        assert self.shape_id in schematic.shape_items

        # 1. Check text properties
        item = schematic.shape_items[self.shape_id]
        assert item.toPlainText() == shape_config.text
        assert item.pos().toTuple() == (shape_config.x, shape_config.y)
        assert item.defaultTextColor().toTuple() == shape_config.color.toTuple()

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
        assert model_config.shapes.find_shape(self.shape_id, as_dict=True) == {
            **shape_config.shape_dict,
            **{
                "text": new_text,
                "color": color_widget.value,
            },
        }

        item = schematic.shape_items[self.shape_id]
        assert item.toPlainText() == new_text
        assert item.defaultTextColor().toTuple()[0:3] == color_widget.value

    def is_shape_deleted(
        self, model_config: ModelConfig, schematic: Schematic
    ) -> None:
        """
        Checks that the shape is deleted in the model configuration and schematic.
        :param model_config: The ModelConfig instance.
        :param schematic: The Schematic instance.
        :return: None
        """
        # the shape is removed from the model configuration
        assert model_config.shapes.find_shape(self.shape_id) is None

        # the shape is removed from the items list
        assert self.shape_id not in schematic.shape_items.keys()

        # the shape is removed from the schematic as graphical item
        shape_ids = [
            shape.id
            for shape in schematic.items()
            if isinstance(shape, SchematicText)
        ]
        assert self.shape_id not in shape_ids

    def is_shape_restored(
        self,
        model_config: ModelConfig,
        schematic: Schematic,
        shape_config: BaseShape,
    ) -> None:
        """
        Checks that the shape exists in the model configuration and schematic.
        :param model_config: The ModelConfig instance.
        :param schematic: The Schematic instance.
        :param shape_config: The shape configuration instance.
        :return: None
        """
        assert model_config.shapes.find_shape(self.shape_id) == shape_config
        assert self.shape_id in schematic.shape_items.keys()
        shape_ids = [
            shape.id
            for shape in schematic.items()
            if isinstance(shape, SchematicText)
        ]
        assert self.shape_id in shape_ids

    def test_delete_text_shape(self, qtbot, init_window) -> None:
        """
        Test that the text shape is properly deleted from the schematic and the model
        configuration.
        """
        window, schematic = init_window
        model_config = window.model_config
        shape_config = model_config.shapes.find_shape(self.shape_id)

        panel = schematic.app.toolbar.tabs["Nodes"].panels["Undo"]
        undo_button = panel.buttons["Undo"]
        redo_button = panel.buttons["Redo"]

        # 1. Delete the shape
        shape = schematic.shape_items[self.shape_id]
        shape.on_delete_item()

        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False
        assert model_config.has_changes is True
        self.is_shape_deleted(model_config, schematic)

        # 2. Test undo operation
        assert window.undo_stack.canUndo() is True
        undo_command: DeleteItemCommand = window.undo_stack.command(0)
        assert undo_command.deleted_shape_configs == [shape_config]

        # undo
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True
        self.is_shape_restored(model_config, schematic, shape_config)

        # 3. Change the shape configuration and test that's later restored
        shape.on_edit_shape()
        # noinspection PyTypeChecker
        dialog_form: ShapeDialogForm = window.findChild(ShapeDialogForm)
        dialog_form.find_field_by_name("text").widget.setText(
            "I changed the label"
        )
        font_size_widget: SpinBox = dialog_form.find_field_by_name(
            "font_size"
        ).widget
        font_size_widget.setValue(40)
        qtbot.mouseClick(dialog_form.save_button, Qt.MouseButton.LeftButton)

        # 4. Test redo and undo operation again
        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False
        self.is_shape_deleted(model_config, schematic)

        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True

        shape_config.shape_dict["text"] = "I changed the label"
        shape_config.shape_dict["font_size"] = 40
        shape_config.shape_dict["color"] = tuple(
            shape_config.shape_dict["color"]
        )
        self.is_shape_restored(model_config, schematic, shape_config)
