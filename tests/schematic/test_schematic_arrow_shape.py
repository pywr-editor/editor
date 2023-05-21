from math import sqrt
from typing import Tuple

import pytest
from PySide6 import QtCore, QtGui
from PySide6.QtCore import QEvent, QMimeData, QPoint, QPointF, Qt, QTimer
from PySide6.QtGui import QDragEnterEvent

from pywr_editor import MainWindow
from pywr_editor.form import ColorPickerWidget
from pywr_editor.model import LineArrowShape
from pywr_editor.schematic import ResizeShapeCommand, Schematic
from pywr_editor.schematic.commands.add_shape_command import AddShapeCommand
from pywr_editor.schematic.shapes.arrow_shape import Handles, SchematicArrow
from pywr_editor.schematic.shapes.shape_dialogs import ShapeDialogForm
from pywr_editor.widgets import SpinBox
from tests.schematic.test_schematic_rectangle_shape import TestSchematicRectangleShape
from tests.utils import close_message_box, resolve_model_path

init_source_point = QPoint(50, 50)
init_target_point = QPointF(155, 232)


class TestSchematicArrowShape:
    model_file = resolve_model_path("model_1.json")
    shape_id = "e3Ad60e"

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

    def test_load_and_edit(self, qtbot, init_window):
        """
        Test that the arrow shape is properly load on the schematic and, when edited,
        its new configuration is saved.
        """
        window, schematic = init_window
        model_config = window.model_config
        shape_config: LineArrowShape = model_config.shapes.find_shape(self.shape_id)
        assert self.shape_id in schematic.shape_items

        # 1. Check shape properties
        item: SchematicArrow = schematic.shape_items[self.shape_id]
        line = item.line()
        assert item.pos().toTuple() == tuple([shape_config.x, shape_config.y])
        assert round(line.length(), 3) == shape_config.length
        assert round(line.angle(), 3) == shape_config.angle

        # 2. Change the border colour and size
        item.on_edit_shape()
        # noinspection PyTypeChecker
        form: ShapeDialogForm = window.findChild(ShapeDialogForm)

        border_size_field: SpinBox = form.find_field_by_name("border_size").widget
        border_size_field.setValue(3)
        color_widget: ColorPickerWidget = form.find_field_by_name("border_color").widget
        color_widget.value = (80, 80, 80)

        # 3. Send form and check the model config and schematic item
        form.save()
        assert model_config.has_changes is True

        shape_config.shape_dict["border_color"] = color_widget.value
        shape_config.shape_dict["border_size"] = border_size_field.value()
        assert (
            model_config.shapes.find_shape(self.shape_id, as_dict=True)
            == shape_config.shape_dict
        )

    def test_add(self, qtbot, init_window):
        """
        Test when a new shape is added to the schematic.
        """
        window, schematic = init_window
        model_config = window.model_config
        item_count = len(schematic.shape_items)
        panel = schematic.app.toolbar.tabs["Operations"].panels["Undo"]
        undo_button = panel.buttons["Undo"]
        redo_button = panel.buttons["Redo"]

        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is False

        # 1. Drop a text
        mime_data = QMimeData()
        mime_data.setText("Shape.ArrowShape")

        # start the drop event
        scene_pos = QPoint(100, 50)
        event = QDragEnterEvent(
            scene_pos,
            Qt.DropAction.CopyAction,
            mime_data,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
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
        assert model_config.shapes.find_shape_index_by_id(new_shape_id) is not None
        shape_config = model_config.shapes.find_shape(new_shape_id)

        # 3. Change shape config
        schematic.shape_items[new_shape_id].on_edit_shape()
        # noinspection PyTypeChecker
        dialog_form: ShapeDialogForm = window.findChild(ShapeDialogForm)
        border_size_widget: SpinBox = dialog_form.find_field_by_name(
            "border_size"
        ).widget
        border_size_widget.setValue(4)
        qtbot.mouseClick(dialog_form.save_button, Qt.MouseButton.LeftButton)
        dialog_form.close()

        # 4. Test undo
        undo_command: AddShapeCommand = window.undo_stack.command(0)
        assert undo_command.added_shape_config == shape_config
        assert undo_command.tracker_shape_config is None

        # undo
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True
        TestSchematicRectangleShape.is_shape_deleted(
            model_config, schematic, new_shape_id, SchematicArrow
        )

        # 5. Test redo operation - the new configuration is restored
        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False

        shape_config.shape_dict["border_size"] = 4
        TestSchematicRectangleShape.is_shape_restored(
            model_config, schematic, shape_config, SchematicArrow
        )

        # 6. Delete again
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True
        TestSchematicRectangleShape.is_shape_deleted(
            model_config, schematic, new_shape_id, SchematicArrow
        )

    @pytest.mark.parametrize(
        "handle, handle_point, target_point",
        [
            # 1st quadrant
            (
                Handles.SOURCE_POINT.value,
                init_source_point,
                QPoint(100, 100),
            ),
            (
                Handles.TARGET_POINT.value,
                init_target_point,
                QPoint(9, 9),
            ),
            # to 2nd quadrant
            (
                Handles.SOURCE_POINT.value,
                init_source_point,
                QPoint(300, 40),
            ),
            (
                Handles.TARGET_POINT.value,
                init_target_point,
                QPoint(190, 290),
            ),
            # to 3rd quadrant
            (
                Handles.SOURCE_POINT.value,
                init_source_point,
                QPoint(190, 290),
            ),
            (
                Handles.TARGET_POINT.value,
                init_target_point,
                QPoint(200, 290),
            ),
            # to 4th quadrant
            (
                Handles.SOURCE_POINT.value,
                init_source_point,
                QPoint(40, 100),
            ),
            (
                Handles.TARGET_POINT.value,
                init_target_point,
                QPoint(10, 150),
            ),
        ],
    )
    def test_resize(self, qtbot, init_window, handle, handle_point, target_point):
        """
        Tests that, when an arrow is resized, the shape is correctly resized using
        its handles and the new size is updated. This also tests the undo/redo command.
        """
        # Initial position p1 = (20, 20)  p2 = (125, 201.865)
        window, schematic = init_window
        model_config = window.model_config

        panel = schematic.app.toolbar.tabs["Operations"].panels["Undo"]
        undo_button = panel.buttons["Undo"]
        redo_button = panel.buttons["Redo"]

        shape_item: SchematicArrow = schematic.shape_items[self.shape_id]
        shape_item.setSelected(True)
        handle_pos = schematic.mapFromScene(handle_point)

        shape_line = shape_item.line()
        init_p1 = shape_item.mapToScene(shape_line.p1())
        init_p2 = shape_item.mapToScene(shape_line.p2())
        init_length = round(shape_line.length(), 3)
        init_angle = round(shape_line.angle(), 3)

        # 1. Move the handle to the target position to resize the shape
        qtbot.mouseMove(schematic.viewport(), handle_pos)
        qtbot.mousePress(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            handle_pos,
        )
        assert shape_item.selected_handle is handle

        # mouse position is in local coordinates
        assert shape_item.mapToScene(shape_item.pressed_mouse_pos) == handle_point
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
        shape_line = shape_item.line()
        if handle == Handles.SOURCE_POINT.value:
            dp = init_p2 - target_point
        else:
            dp = init_p1 - target_point
        assert round(shape_line.length(), 3) == round(
            sqrt(dp.x() ** 2 + dp.y() ** 2), 3
        )
        new_length = round(shape_line.length(), 3)
        new_angle = round(shape_line.angle(), 3)

        if handle == Handles.SOURCE_POINT.value:
            local_point = shape_item.mapToScene(shape_line.p1())
        else:
            local_point = shape_item.mapToScene(shape_line.p2())

        assert local_point.x() == target_point.x()
        assert local_point.y() == target_point.y()

        # 3. Check the model configuration
        assert model_config.has_changes is True
        shape_config: LineArrowShape = model_config.shapes.find_shape(
            shape_id=self.shape_id
        )
        assert shape_config.x == round(shape_item.mapToScene(shape_line.x1(), 0).x(), 5)
        assert shape_config.y == round(shape_item.mapToScene(0, shape_line.y1()).y(), 5)
        assert shape_config.angle == round(shape_line.angle(), 3)
        assert shape_config.length == round(shape_line.length(), 3)

        # 4. Check undo command
        undo_command: ResizeShapeCommand = window.undo_stack.command(0)
        assert undo_command.prev_other_info == {
            "length": init_length,
            "angle": init_angle,
        }
        assert undo_command.prev_pos == init_source_point.toTuple()
        assert undo_command.updated_other_info == {
            "length": round(shape_config.length, 3),
            "angle": round(shape_config.angle, 3),
        }
        assert undo_command.updated_pos == (
            shape_config.x,
            shape_config.y,
        )
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False

        # 5. Change the border size
        shape_item.on_edit_shape()
        # noinspection PyTypeChecker
        form: ShapeDialogForm = window.findChild(ShapeDialogForm)
        border_size_field: SpinBox = form.find_field_by_name("border_size").widget
        border_size_field.setValue(1)

        form.save()
        new_shape_dict = shape_config.shape_dict.copy()
        del new_shape_dict["border_size"]
        assert (
            model_config.shapes.find_shape(self.shape_id, as_dict=True)
            == new_shape_dict
        )

        # 6. Test redo command
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True

        shape_config = model_config.shapes.find_shape(shape_id=self.shape_id)
        assert shape_config.x == init_source_point.x()
        assert shape_config.y == init_source_point.y()
        assert shape_config.length == init_length
        assert shape_config.angle == init_angle
        # check that the new style is preserved
        assert "border_size" not in shape_config.shape_dict

        shape_item = schematic.shape_items[self.shape_id]
        assert (
            shape_item.mapToScene(shape_item.line().x1(), 0).x()
            == init_source_point.x()
        )
        assert (
            shape_item.mapToScene(0, shape_item.line().y1()).y()
            == init_source_point.y()
        )
        assert round(shape_item.line().length(), 3) == init_length
        assert round(shape_item.line().angle(), 3) == init_angle

        # 7. Test Redo command
        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False
        shape_item = schematic.shape_items[self.shape_id]

        # check model config
        shape_config = model_config.shapes.find_shape(shape_id=self.shape_id)
        assert shape_config.x == undo_command.updated_pos[0]
        assert shape_config.y == undo_command.updated_pos[1]
        assert shape_config.length == new_length
        assert shape_config.angle == new_angle
        # check that the new style is preserved
        assert "border_size" not in shape_config.shape_dict

        # check schematic item
        assert (
            shape_item.mapToScene(shape_item.line().x1(), 0).x()
            == undo_command.updated_pos[0]
        )
        assert (
            shape_item.mapToScene(0, shape_item.line().y1()).y()
            == undo_command.updated_pos[1]
        )
        assert round(shape_item.line().length(), 3) == new_length
        assert round(shape_item.line().angle(), 3) == new_angle

    @pytest.mark.parametrize(
        "handle, handle_point, target_point, expected_target",
        [
            # source handle
            (
                Handles.SOURCE_POINT.value,
                init_source_point,
                QPoint(-100, -10),
                QPointF(SchematicArrow.handle_size, SchematicArrow.handle_size),
            ),
            (
                Handles.SOURCE_POINT.value,
                init_source_point,
                QPoint(1900, 40),
                QPointF(1900 - SchematicArrow.handle_size, 40),
            ),
            (
                Handles.SOURCE_POINT.value,
                init_source_point,
                QPoint(50, 3000),
                QPointF(50, 1450 - SchematicArrow.handle_size),
            ),
            # target handle
            (
                Handles.TARGET_POINT.value,
                init_target_point,
                QPoint(-100, -10),
                QPointF(SchematicArrow.handle_size, SchematicArrow.handle_size),
            ),
            (
                Handles.TARGET_POINT.value,
                init_target_point,
                QPoint(1900, 40),
                QPointF(1900 - SchematicArrow.handle_size, 40),
            ),
            (
                Handles.TARGET_POINT.value,
                init_target_point,
                QPoint(50, 3000),
                QPointF(50, 1450 - SchematicArrow.handle_size),
            ),
        ],
    )
    def test_resize_canvas_constraints(
        self,
        qtbot,
        init_window,
        handle,
        handle_point,
        target_point,
        expected_target,
    ):
        """
        Tests that, when the shape is resized outside the canvas limits, the arrow
        is reshaped to fit into the schematic. The handle is aligned to the canvas edge
        so that the line point is at a distance of SchematicArrow.handle_size pixels.
        """
        window, schematic = init_window

        shape_item: SchematicArrow = schematic.shape_items[self.shape_id]
        shape_item.setSelected(True)
        handle_pos = schematic.mapFromScene(handle_point)

        qtbot.mouseMove(schematic.viewport(), handle_pos)
        qtbot.mousePress(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            handle_pos,
        )
        assert shape_item.selected_handle is handle
        assert shape_item.mapToScene(shape_item.pressed_mouse_pos) == (handle_point)
        qtbot.mouseMove(
            schematic.viewport(),
            schematic.mapFromScene(target_point),
        )
        qtbot.mouseRelease(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        if handle == Handles.SOURCE_POINT.value:
            assert shape_item.mapToScene(shape_item.line().p1()) == expected_target
        else:
            assert shape_item.mapToScene(shape_item.line().p2()) == expected_target

    @pytest.mark.parametrize(
        "handle, handle_point, target_point",
        [
            # source handle - all quadrants
            (Handles.SOURCE_POINT.value, init_source_point, QPoint(130, 210)),
            (Handles.SOURCE_POINT.value, init_source_point, QPoint(170, 210)),
            (Handles.SOURCE_POINT.value, init_source_point, QPoint(170, 240)),
            (Handles.SOURCE_POINT.value, init_source_point, QPoint(110, 240)),
            # target handle - all quadrants
            (Handles.TARGET_POINT.value, init_target_point, QPoint(20, 20)),
            (Handles.TARGET_POINT.value, init_target_point, QPoint(50, 30)),
            (Handles.TARGET_POINT.value, init_target_point, QPoint(60, 60)),
            (Handles.TARGET_POINT.value, init_target_point, QPoint(30, 50)),
        ],
    )
    def test_non_negative_constraints(
        self,
        qtbot,
        init_window,
        handle,
        handle_point,
        target_point,
    ):
        """
        Tests that the line maintains the minimum length when it is resized.
        """
        window, schematic = init_window

        shape_item: SchematicArrow = schematic.shape_items[self.shape_id]
        shape_item.setSelected(True)
        handle_pos = schematic.mapFromScene(handle_point)

        qtbot.mouseMove(schematic.viewport(), handle_pos)
        qtbot.mousePress(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            handle_pos,
        )
        assert shape_item.selected_handle is handle
        assert shape_item.pressed_mouse_pos == shape_item.mapFromScene(handle_point)
        qtbot.mouseMove(
            schematic.viewport(),
            schematic.mapFromScene(target_point),
        )
        qtbot.mouseRelease(
            schematic.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        assert round(shape_item.line().length(), 3) == shape_item.min_line_length
