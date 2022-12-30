from typing import Tuple

import pytest
from PySide6 import QtGui
from PySide6.QtCore import QEvent, QMimeData, QPoint, Qt, QTimer
from PySide6.QtGui import QDragEnterEvent
from PySide6.QtWidgets import QLineEdit

from pywr_editor import MainWindow
from pywr_editor.form import ColorPickerWidget
from pywr_editor.model import BaseShape, ModelConfig, TextShape
from pywr_editor.schematic import (
    AddShapeCommand,
    DeleteItemCommand,
    ResizeShapeCommand,
    Schematic,
    SchematicText,
)
from pywr_editor.schematic.shapes.rectangle_shape import (
    Handles,
    SchematicRectangle,
)
from pywr_editor.schematic.shapes.shape_dialogs import ShapeDialogForm
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

    @staticmethod
    def is_shape_deleted(
        model_config: ModelConfig, schematic: Schematic, shape_id: str
    ) -> None:
        """
        Checks that the shape is deleted in the model configuration and schematic.
        :param model_config: The ModelConfig instance.
        :param schematic: The Schematic instance.
        :param shape_id: The shape ID to check.
        :return: None
        """
        # the shape is removed from the model configuration
        assert model_config.shapes.find_shape(shape_id) is None

        # the shape is removed from the items list
        assert shape_id not in schematic.shape_items.keys()

        # the shape is removed from the schematic as graphical item
        shape_ids = [
            shape.id
            for shape in schematic.items()
            if isinstance(shape, SchematicText)
        ]
        assert shape_id not in shape_ids

    @staticmethod
    def is_shape_restored(
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
        assert model_config.shapes.find_shape(shape_config.id) == shape_config
        assert shape_config.id in schematic.shape_items.keys()
        shape_ids = [
            shape.id
            for shape in schematic.items()
            if isinstance(shape, SchematicText)
        ]
        assert shape_config.id in shape_ids

    def test_delete_text_shape(self, qtbot, init_window) -> None:
        """
        Test that the text shape is properly deleted from the schematic and the model
        configuration.
        """
        window, schematic = init_window
        model_config = window.model_config
        shape_config = model_config.shapes.find_shape(self.shape_id)

        panel = schematic.app.toolbar.tabs["Schematic"].panels["Undo"]
        undo_button = panel.buttons["Undo"]
        redo_button = panel.buttons["Redo"]

        # 1. Delete the shape
        shape = schematic.shape_items[self.shape_id]
        shape.on_delete_item()

        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False
        assert model_config.has_changes is True
        self.is_shape_deleted(model_config, schematic, self.shape_id)

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
        self.is_shape_deleted(model_config, schematic, self.shape_id)

        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True

        shape_config.shape_dict["text"] = "I changed the label"
        shape_config.shape_dict["font_size"] = 40
        shape_config.shape_dict["color"] = tuple(
            shape_config.shape_dict["color"]
        )
        self.is_shape_restored(model_config, schematic, shape_config)

    def test_add_new_text_shape(self, qtbot, init_window):
        """
        Test when a new shape is added to the schematic.
        """
        window, schematic = init_window
        model_config = window.model_config
        item_count = len(schematic.shape_items)
        panel = schematic.app.toolbar.tabs["Schematic"].panels["Undo"]
        undo_button = panel.buttons["Undo"]
        redo_button = panel.buttons["Redo"]

        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is False

        # 1. Drop a text
        mime_data = QMimeData()
        mime_data.setText("Shape.TextShape")

        # start the drop event
        scene_pos = QPoint(100, 50)
        event = QDragEnterEvent(
            scene_pos,
            Qt.DropAction.CopyAction,
            mime_data,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        from PySide6 import QtCore

        QtCore.QCoreApplication.sendEvent(schematic.viewport(), event)

        # drop the shape
        event = QtGui.QDropEvent(
            scene_pos,
            Qt.DropAction.MoveAction,
            mime_data,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            QEvent.Drop,
        )
        QtCore.QCoreApplication.sendEvent(schematic.viewport(), event)

        # 2. Check that the new shape is in the schematic
        new_item_count = len(schematic.shape_items)
        new_shape_id = list(schematic.shape_items.keys())[-1]
        assert new_item_count == item_count + 1

        assert model_config.has_changes is True
        # the shape is in the model configuration
        assert (
            model_config.shapes.find_shape_index_by_id(new_shape_id) is not None
        )
        shape_config = model_config.shapes.find_shape(new_shape_id)

        # 3. Change shape config
        schematic.shape_items[new_shape_id].on_edit_shape()
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

        # 4. Test undo
        undo_command: AddShapeCommand = window.undo_stack.command(0)
        assert undo_command.added_shape_config == shape_config
        assert undo_command.tracker_shape_config is None
        print(shape_config)

        # undo
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True
        self.is_shape_deleted(model_config, schematic, new_shape_id)

        # 5. Test redo operation - the new configuration is restored
        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False

        shape_config.shape_dict["text"] = "I changed the label"
        shape_config.shape_dict["font_size"] = 40

        self.is_shape_restored(model_config, schematic, shape_config)

        # 6. Delete again
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True
        self.is_shape_deleted(model_config, schematic, new_shape_id)

    @pytest.mark.parametrize(
        "handle, handle_point, target_point, delta_width, delta_height, rect_check_point",  # noqa: E501
        [
            # corner points
            (
                Handles.TOP_LEFT.value,
                QPoint(800, 800),
                QPoint(700, 600),
                100,
                200,
                "topLeft",
            ),
            (
                Handles.TOP_RIGHT.value,
                QPoint(1100, 800),
                QPoint(1500, 750),
                400,
                50,
                "topRight",
            ),
            (
                Handles.BOTTOM_LEFT.value,
                QPoint(800, 1100),
                QPoint(300, 1300),
                500,
                200,
                "bottomLeft",
            ),
            (
                Handles.BOTTOM_RIGHT.value,
                QPoint(1100, 1100),
                QPoint(1200, 1200),
                100,
                100,
                "bottomRight",
            ),
            # middle points
            (
                Handles.TOP_MIDDLE.value,
                QPoint(950, 800),
                QPoint(950, 700),
                0,
                100,
                ["center", "topLeft"],
            ),
            (
                Handles.MIDDLE_RIGHT.value,
                QPoint(1100, 950),
                QPoint(1300, 950),
                200,
                0,
                ["topRight", "center"],
            ),
            (
                Handles.BOTTOM_MIDDLE.value,
                QPoint(950, 1100),
                QPoint(950, 1000),
                0,
                -100,
                ["center", "bottomRight"],
            ),
            (
                Handles.MIDDLE_LEFT.value,
                QPoint(800, 950),
                QPoint(850, 950),
                -50,
                0,
                ["topLeft", "center"],
            ),
        ],
    )
    def test_resize_rectangle_shape(
        self,
        qtbot,
        init_window,
        handle,
        handle_point,
        target_point,
        delta_width,
        delta_height,
        rect_check_point,
    ):
        """
        Tests that, when a rectangle is resized, the shape is correctly resized using
        its handles and the new size is updated. This also tests the undo/redo command.
        """
        window, schematic = init_window
        model_config = window.model_config

        panel = schematic.app.toolbar.tabs["Schematic"].panels["Undo"]
        undo_button = panel.buttons["Undo"]
        redo_button = panel.buttons["Redo"]

        shape_id = "466eaX"
        shape_item: SchematicRectangle = schematic.shape_items[shape_id]
        shape_item.setSelected(True)
        or_width = shape_item.rect().width()
        or_height = shape_item.rect().height()
        handle_pos = schematic.mapFromScene(handle_point)

        # 1. Move the handle to the target position to resize the rectangle
        qtbot.mouseMove(schematic.viewport(), handle_pos)
        qtbot.mousePress(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            handle_pos,
        )
        assert shape_item.selected_handle is handle
        assert shape_item.pressed_mouse_pos == handle_point
        qtbot.mouseMove(
            schematic.viewport(),
            schematic.mapFromScene(target_point),
        )
        qtbot.mouseRelease(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        # 2. Check that the shape was resized on the schematic
        if isinstance(rect_check_point, list):  # handle middle points
            assert (
                getattr(shape_item.rect(), rect_check_point[0])().x()
                == target_point.x()
            )
            assert (
                getattr(shape_item.rect(), rect_check_point[1])().y()
                == target_point.y()
            )
        else:
            assert (
                getattr(shape_item.rect(), rect_check_point)() == target_point
            )
        assert shape_item.rect().width() == or_width + delta_width
        assert shape_item.rect().height() == or_height + delta_height

        # 3. Check the model configuration
        assert model_config.has_changes is True
        shape_dict = model_config.shapes.find_shape(
            shape_id=shape_id, as_dict=True
        )
        assert shape_dict["width"] == round(shape_item.rect().width(), 5)
        assert shape_dict["height"] == round(shape_item.rect().height(), 5)

        # 4. Check undo command
        undo_command: ResizeShapeCommand = window.undo_stack.command(0)

        assert undo_command.prev_size == (300, 300)
        assert undo_command.updated_size == (
            shape_dict["width"],
            shape_dict["height"],
        )
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False

        # 5. Test redo command
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True

        shape_dict = model_config.shapes.find_shape(
            shape_id=shape_id, as_dict=True
        )
        assert shape_dict["width"] == 300
        assert shape_dict["height"] == 300

        shape_item = schematic.shape_items[shape_id]
        assert shape_item.rect().width() == 300
        assert shape_item.rect().height() == 300

        # 6. Test Redo command
        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False

        shape_dict = model_config.shapes.find_shape(
            shape_id=shape_id, as_dict=True
        )
        assert shape_dict["width"] == or_width + delta_width
        assert shape_dict["height"] == or_height + delta_height

        shape_item = schematic.shape_items[shape_id]
        assert shape_item.rect().width() == or_width + delta_width
        assert shape_item.rect().height() == or_height + delta_height

    @pytest.mark.parametrize(
        "handle, handle_point, target_point, delta_width, delta_height",
        [
            # corner points
            (
                Handles.TOP_LEFT.value,
                QPoint(800, 800),
                QPoint(-100, -10),
                800,
                800,
            ),
            (
                Handles.TOP_RIGHT.value,
                QPoint(1100, 800),
                QPoint(3000, -10),
                800,
                800,
            ),
            (
                Handles.BOTTOM_LEFT.value,
                QPoint(800, 1100),
                QPoint(-100, 3000),
                800,
                350,
            ),
            (
                Handles.BOTTOM_RIGHT.value,
                QPoint(1100, 1100),
                QPoint(5000, 2000),
                800,
                350,
            ),
            # middle points
            (
                Handles.TOP_MIDDLE.value,
                QPoint(950, 800),
                QPoint(950, -10),
                0,
                800,
            ),
            (
                Handles.MIDDLE_RIGHT.value,
                QPoint(1100, 950),
                QPoint(3000, 950),
                800,
                0,
            ),
            (
                Handles.BOTTOM_MIDDLE.value,
                QPoint(950, 1100),
                QPoint(950, 3000),
                0,
                350,
            ),
            (
                Handles.MIDDLE_LEFT.value,
                QPoint(800, 950),
                QPoint(-100, 950),
                800,
                0,
            ),
        ],
    )
    def test_resize_constraints_rectangle_shape(
        self,
        qtbot,
        init_window,
        handle,
        handle_point,
        target_point,
        delta_width,
        delta_height,
    ):
        """
        Tests that, when the shape is resized outside the canvas limits, the rectangle
        is reshaped to fit into the schematic.
        """
        window, schematic = init_window

        shape_id = "466eaX"
        shape_item: SchematicRectangle = schematic.shape_items[shape_id]
        shape_item.setSelected(True)
        or_width = shape_item.rect().width()
        or_height = shape_item.rect().height()
        handle_pos = schematic.mapFromScene(handle_point)

        qtbot.mouseMove(schematic.viewport(), handle_pos)
        qtbot.mousePress(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            handle_pos,
        )
        assert shape_item.selected_handle is handle
        assert shape_item.pressed_mouse_pos == handle_point
        qtbot.mouseMove(
            schematic.viewport(),
            schematic.mapFromScene(target_point),
        )
        qtbot.mouseRelease(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        if delta_width:
            assert (
                shape_item.rect().width()
                == or_width + delta_width + shape_item.handle_space
            )
        if delta_height:
            assert (
                shape_item.rect().height()
                == or_height + delta_height + shape_item.handle_space
            )

        match handle:
            case Handles.TOP_LEFT.value:
                assert shape_item.rect().topLeft().toTuple() == tuple(
                    [-shape_item.handle_space] * 2
                )
            case Handles.TOP_RIGHT.value:
                assert shape_item.rect().topRight().toTuple() == tuple(
                    [
                        schematic.schematic_width + shape_item.handle_space,
                        -shape_item.handle_space,
                    ]
                )
            case Handles.BOTTOM_LEFT.value:
                assert shape_item.rect().bottomLeft().toTuple() == tuple(
                    [
                        -shape_item.handle_space,
                        schematic.schematic_height + shape_item.handle_space,
                    ]
                )
            case Handles.BOTTOM_RIGHT.value:
                assert shape_item.rect().bottomRight().toTuple() == tuple(
                    [
                        schematic.schematic_width + shape_item.handle_space,
                        schematic.schematic_height + shape_item.handle_space,
                    ]
                )
            case Handles.TOP_MIDDLE.value:
                assert shape_item.rect().top() == -shape_item.handle_space
            case Handles.MIDDLE_RIGHT.value:
                assert (
                    shape_item.rect().right()
                    == schematic.schematic_width + shape_item.handle_space
                )
            case Handles.BOTTOM_MIDDLE.value:
                assert (
                    shape_item.rect().bottom()
                    == schematic.schematic_height + shape_item.handle_space
                )
            case Handles.MIDDLE_LEFT.value:
                assert shape_item.rect().left() == -shape_item.handle_space
            case _:
                assert False

    @pytest.mark.parametrize(
        "handle, handle_point, target_point, min_width, min_height",
        [
            # corner points
            (
                Handles.TOP_LEFT.value,
                QPoint(800, 800),
                QPoint(1200, 1200),
                True,
                True,
            ),
            (
                Handles.TOP_RIGHT.value,
                QPoint(1100, 800),
                QPoint(0, 2000),
                True,
                True,
            ),
            (
                Handles.BOTTOM_LEFT.value,
                QPoint(800, 1100),
                QPoint(2000, 0),
                True,
                True,
            ),
            (
                Handles.BOTTOM_RIGHT.value,
                QPoint(1100, 1100),
                QPoint(0, 0),
                True,
                True,
            ),
            # middle points
            (
                Handles.TOP_MIDDLE.value,
                QPoint(950, 800),
                QPoint(950, 2000),
                False,
                True,
            ),
            (
                Handles.MIDDLE_RIGHT.value,
                QPoint(1100, 950),
                QPoint(0, 950),
                True,
                False,
            ),
            (
                Handles.BOTTOM_MIDDLE.value,
                QPoint(950, 1100),
                QPoint(950, 0),
                False,
                True,
            ),
            (
                Handles.MIDDLE_LEFT.value,
                QPoint(800, 950),
                QPoint(2000, 950),
                True,
                False,
            ),
        ],
    )
    def test_not_negative_constraints_rectangle_shape(
        self,
        qtbot,
        init_window,
        handle,
        handle_point,
        target_point,
        min_width,
        min_height,
    ):
        """
        Tests that, when one rectangle edge is moved the opposite edge, the rectangle
        keeps a minimum size.
        """
        window, schematic = init_window

        shape_id = "466eaX"
        shape_item: SchematicRectangle = schematic.shape_items[shape_id]
        shape_item.setSelected(True)
        or_width = shape_item.rect().width()
        or_height = shape_item.rect().height()
        handle_pos = schematic.mapFromScene(handle_point)

        qtbot.mouseMove(schematic.viewport(), handle_pos)
        qtbot.mousePress(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            handle_pos,
        )
        assert shape_item.selected_handle is handle
        assert shape_item.pressed_mouse_pos == handle_point
        qtbot.mouseMove(
            schematic.viewport(),
            schematic.mapFromScene(target_point),
        )
        qtbot.mouseRelease(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        if min_width:  # rectangle width was resized
            assert (
                shape_item.rect().width()
                == shape_item.min_rect_width + shape_item.handle_space
            )
        else:  # the width was not changed
            assert shape_item.rect().width() == or_width

        if min_height:  # rectangle height was resized
            assert (
                shape_item.rect().height()
                == shape_item.min_rect_height + shape_item.handle_space
            )
        else:  # the width was not changed
            assert shape_item.rect().height() == or_height
