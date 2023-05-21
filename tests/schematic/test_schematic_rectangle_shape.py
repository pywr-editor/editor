from typing import Tuple, Type

import pytest
from PySide6 import QtCore, QtGui
from PySide6.QtCore import QEvent, QMimeData, QPoint, Qt, QTimer
from PySide6.QtGui import QDragEnterEvent

from pywr_editor import MainWindow
from pywr_editor.form import ColorPickerWidget
from pywr_editor.model import LineArrowShape, ModelConfig, RectangleShape
from pywr_editor.schematic import ResizeShapeCommand, Schematic
from pywr_editor.schematic.commands.add_shape_command import AddShapeCommand
from pywr_editor.schematic.shapes.abstract_schematic_shape import AbstractSchematicShape
from pywr_editor.schematic.shapes.rectangle_shape import Handles, SchematicRectangle
from pywr_editor.schematic.shapes.shape_dialogs import ShapeDialogForm
from pywr_editor.widgets import SpinBox
from tests.utils import close_message_box, resolve_model_path


class TestSchematicRectangleShape:
    model_file = resolve_model_path("model_1.json")
    shape_id = "466eaX"

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
        Test that the rectangle shape is properly load on the schematic and, when
        edited, its new configuration is saved.
        """
        window, schematic = init_window
        model_config = window.model_config
        shape_config: RectangleShape = model_config.shapes.find_shape(self.shape_id)
        assert self.shape_id in schematic.shape_items

        # 1. Check shape properties
        item: SchematicRectangle = schematic.shape_items[self.shape_id]
        assert item.rect().width() == shape_config.width
        assert item.rect().height() == shape_config.height
        assert item.pos().toTuple() == (shape_config.x, shape_config.y)

        # 2. Change the border colour and size
        item.on_edit_shape()
        # noinspection PyTypeChecker
        form: ShapeDialogForm = window.findChild(ShapeDialogForm)

        border_size_field: SpinBox = form.find_field_by_name("border_size").widget
        border_size_field.setValue(1)
        color_widget: ColorPickerWidget = form.find_field_by_name("border_color").widget
        color_widget.value = (80, 80, 80)

        # 3. Send form and check the model config and schematic item
        form.save()
        assert model_config.has_changes is True

        shape_config.shape_dict["border_color"] = color_widget.value
        del shape_config.shape_dict["border_size"]
        assert (
            model_config.shapes.find_shape(self.shape_id, as_dict=True)
            == shape_config.shape_dict
        )

    @staticmethod
    def is_shape_deleted(
        model_config: ModelConfig,
        schematic: Schematic,
        shape_id: str,
        schematic_item_type: Type[AbstractSchematicShape] = SchematicRectangle,
    ) -> None:
        """
        Checks that the shape is deleted in the model configuration and schematic.
        :param model_config: The ModelConfig instance.
        :param schematic: The Schematic instance.
        :param shape_id: The shape ID to check.
        :param schematic_item_type: The type of schematic item. Default to
        SchematicRectangle.
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
            if isinstance(shape, schematic_item_type)
        ]
        assert shape_id not in shape_ids

    @staticmethod
    def is_shape_restored(
        model_config: ModelConfig,
        schematic: Schematic,
        shape_config: RectangleShape | LineArrowShape,
        schematic_item_type: Type[AbstractSchematicShape] = SchematicRectangle,
    ) -> None:
        """
        Checks that the shape exists in the model configuration and schematic.
        :param model_config: The ModelConfig instance.
        :param schematic: The Schematic instance.
        :param shape_config: The shape configuration instance.

        :param schematic_item_type: The type of schematic item. Default to
        SchematicRectangle.
        :return: None
        """
        assert model_config.shapes.find_shape(shape_config.id) == shape_config
        assert shape_config.id in schematic.shape_items.keys()
        shape_ids = [
            shape.id
            for shape in schematic.items()
            if isinstance(shape, schematic_item_type)
        ]
        assert shape_config.id in shape_ids

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
        mime_data.setText("Shape.RectangleShape")

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

        # 4. Test undo
        undo_command: AddShapeCommand = window.undo_stack.command(0)
        assert undo_command.added_shape_config == shape_config
        assert undo_command.tracker_shape_config is None

        # undo
        qtbot.mouseClick(undo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is False
        assert redo_button.isEnabled() is True
        self.is_shape_deleted(model_config, schematic, new_shape_id)

        # 5. Test redo operation - the new configuration is restored
        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False

        shape_config.shape_dict["border_size"] = 4
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
    def test_resize(
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

        panel = schematic.app.toolbar.tabs["Operations"].panels["Undo"]
        undo_button = panel.buttons["Undo"]
        redo_button = panel.buttons["Redo"]

        shape_item: SchematicRectangle = schematic.shape_items[self.shape_id]
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
        shape_rect = shape_item.rect()
        if isinstance(rect_check_point, list):  # handle middle points
            local_point = getattr(shape_rect, rect_check_point[0])()
            assert shape_item.mapToScene(local_point).x() == target_point.x()

            local_point = getattr(shape_rect, rect_check_point[1])()
            assert shape_item.mapToScene(local_point).y() == target_point.y()
        else:
            local_point = getattr(shape_rect, rect_check_point)()
            assert shape_item.mapToScene(local_point) == target_point
        assert shape_rect.width() == or_width + delta_width
        assert shape_rect.height() == or_height + delta_height

        # 3. Check the model configuration
        assert model_config.has_changes is True
        shape_config: RectangleShape = model_config.shapes.find_shape(
            shape_id=self.shape_id
        )
        assert shape_config.width == round(shape_rect.width(), 5)
        assert shape_config.height == round(shape_rect.height(), 5)
        assert shape_config.x == round(shape_item.mapToScene(shape_rect.x(), 0).x(), 5)
        assert shape_config.y == round(shape_item.mapToScene(0, shape_rect.y()).y(), 5)

        # 4. Check undo command
        undo_command: ResizeShapeCommand = window.undo_stack.command(0)
        assert undo_command.prev_other_info == (300, 300)
        assert undo_command.prev_pos == (800, 800)
        assert undo_command.updated_other_info == (
            shape_config.width,
            shape_config.height,
        )
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
        new_shape_dict["border_color"] = tuple(new_shape_dict["border_color"])
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
        assert shape_config.x == 800
        assert shape_config.y == 800
        assert shape_config.width == 300
        assert shape_config.height == 300
        # check that the new style is preserved
        assert "border_size" not in shape_config.shape_dict

        shape_item = schematic.shape_items[self.shape_id]
        assert shape_item.mapToScene(shape_item.rect().x(), 0).x() == 800
        assert shape_item.mapToScene(0, shape_item.rect().y()).y() == 800
        assert shape_item.rect().width() == 300
        assert shape_item.rect().height() == 300

        # 7. Test Redo command
        qtbot.mouseClick(redo_button, Qt.MouseButton.LeftButton)
        assert undo_button.isEnabled() is True
        assert redo_button.isEnabled() is False
        shape_item = schematic.shape_items[self.shape_id]

        # check model config
        shape_config = model_config.shapes.find_shape(shape_id=self.shape_id)
        assert shape_config.x == undo_command.updated_pos[0]
        assert shape_config.y == undo_command.updated_pos[1]
        assert shape_config.width == or_width + delta_width
        assert shape_config.height == or_height + delta_height
        # check that the new style is preserved
        assert "border_size" not in shape_config.shape_dict

        # check schematic item
        assert (
            shape_item.mapToScene(shape_item.rect().x(), 0).x()
            == undo_command.updated_pos[0]
        )
        assert (
            shape_item.mapToScene(0, shape_item.rect().y()).y()
            == undo_command.updated_pos[1]
        )
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
    def test_resize_canvas_constraints(
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

        shape_item: SchematicRectangle = schematic.shape_items[self.shape_id]
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

        # check rectangle size
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

        # check rectangle position
        match handle:
            case Handles.TOP_LEFT.value:
                assert shape_item.mapToScene(
                    shape_item.rect().topLeft()
                ).toTuple() == tuple([-shape_item.handle_space] * 2)
            case Handles.TOP_RIGHT.value:
                assert shape_item.mapToScene(
                    shape_item.rect().topRight()
                ).toTuple() == tuple(
                    [
                        schematic.schematic_width + shape_item.handle_space,
                        -shape_item.handle_space,
                    ]
                )
            case Handles.BOTTOM_LEFT.value:
                assert shape_item.mapToScene(
                    shape_item.rect().bottomLeft()
                ).toTuple() == tuple(
                    [
                        -shape_item.handle_space,
                        schematic.schematic_height + shape_item.handle_space,
                    ]
                )
            case Handles.BOTTOM_RIGHT.value:
                assert shape_item.mapToScene(
                    shape_item.rect().bottomRight()
                ).toTuple() == tuple(
                    [
                        schematic.schematic_width + shape_item.handle_space,
                        schematic.schematic_height + shape_item.handle_space,
                    ]
                )
            case Handles.TOP_MIDDLE.value:
                assert (
                    shape_item.mapToScene(0, shape_item.rect().top()).y()
                    == -shape_item.handle_space
                )
            case Handles.MIDDLE_RIGHT.value:
                assert (
                    shape_item.mapToScene(shape_item.rect().right(), 0).x()
                    == schematic.schematic_width + shape_item.handle_space
                )
            case Handles.BOTTOM_MIDDLE.value:
                assert (
                    shape_item.mapToScene(0, shape_item.rect().bottom()).y()
                    == schematic.schematic_height + shape_item.handle_space
                )
            case Handles.MIDDLE_LEFT.value:
                assert (
                    shape_item.mapToScene(shape_item.rect().left(), 0).x()
                    == -shape_item.handle_space
                )
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
    def test_non_negative_constraints(
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

        shape_item: SchematicRectangle = schematic.shape_items[self.shape_id]
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
