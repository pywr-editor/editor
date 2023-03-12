from enum import Enum
from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import QPointF, QRectF, Slot
from PySide6.QtGui import QBrush, QPainter, QPainterPath, QPen, Qt
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem

from pywr_editor.form import ColorPickerWidget
from pywr_editor.model import RectangleShape
from pywr_editor.style import Color
from pywr_editor.widgets import ContextualMenu

from ..commands.resize_shape_command import ResizeShapeCommand
from .abstract_schematic_shape import AbstractSchematicShape
from .shape_dialogs import ShapeDialog

if TYPE_CHECKING:
    from pywr_editor.schematic import Schematic


class Handles(Enum):
    TOP_LEFT = 0
    TOP_MIDDLE = 1
    TOP_RIGHT = 2
    MIDDLE_LEFT = 3
    MIDDLE_RIGHT = 4
    BOTTOM_LEFT = 5
    BOTTOM_MIDDLE = 6
    BOTTOM_RIGHT = 7


class SchematicRectangle(AbstractSchematicShape, QGraphicsRectItem):
    """
    This widgets renders a rectangle onto the schematic.
    """

    handle_size = 8
    """ The size of the handle """
    handle_space = -4
    """ Reduce the handle interactive area by the provided space """
    handle_cursor_map = {
        Handles.TOP_LEFT.value: Qt.CursorShape.SizeFDiagCursor,
        Handles.TOP_MIDDLE.value: Qt.CursorShape.SizeVerCursor,
        Handles.TOP_RIGHT.value: Qt.CursorShape.SizeBDiagCursor,
        Handles.MIDDLE_LEFT.value: Qt.CursorShape.SizeHorCursor,
        Handles.MIDDLE_RIGHT.value: Qt.CursorShape.SizeHorCursor,
        Handles.BOTTOM_LEFT.value: Qt.CursorShape.SizeBDiagCursor,
        Handles.BOTTOM_MIDDLE.value: Qt.CursorShape.SizeVerCursor,
        Handles.BOTTOM_RIGHT.value: Qt.CursorShape.SizeFDiagCursor,
    }
    """ The map of the mouse cursors to use for each resize handle """
    min_rect_width = 50
    """ The minimum width of the rectangle """
    min_rect_height = 50
    """ The minimum height of the rectangle """

    def __init__(self, shape_id: str, shape: RectangleShape, view: "Schematic"):
        """
        Initialise the rectangle shape.
        :param shape: The RectangleShape instance.
        :param view: The view where to draw the item.
        """
        AbstractSchematicShape.__init__(self, shape_id, shape, view)
        QGraphicsRectItem.__init__(self)

        self.view = view
        self.shape_obj = shape
        self.handles: dict[int, QRectF] = {}
        self.selected_handle = None
        self.pressed_mouse_pos = None
        self.pressed_mouse_rect = None

        # shape styles for the paint method
        self.pen = QPen(shape.border_color)
        self.pen.setWidth(shape.border_size)
        self.brush = QBrush(shape.background_color)

        # allow interaction
        self.setFlag(
            QGraphicsItem.ItemIsMovable,
            self.view.editor_settings.is_schematic_locked is False,
        )
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        # speed up rendering performance
        self.setCacheMode(QGraphicsItem.ItemCoordinateCache)
        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        # set position
        self.setPos(shape.x, shape.y)
        self.setRect(0, 0, shape.width, shape.height)
        self.setZValue(-1)  # place it behind all items

        # store the position after drawing the item
        self.prev_position = self.scenePos().toTuple()
        self.update_handle_position()

    def boundingRect(self) -> PySide6.QtCore.QRectF:
        """
        Returns the bounding rectangle of the shape including the resize handles.
        """
        o = self.handle_size + self.handle_space
        return self.rect().adjusted(-o, -o, o, o)

    def hoverMoveEvent(
        self, event: PySide6.QtWidgets.QGraphicsSceneHoverEvent
    ) -> None:
        """
        Change the cursor when the cursor is on the resize handle.
        :param event: The event instance.
        :return: None
        """
        if self.isSelected():
            handle = self.handle_at(event.pos())
            cursor = (
                Qt.CursorShape.SizeAllCursor
                if handle is None
                else self.handle_cursor_map[handle]
            )
            self.setCursor(cursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(
        self, event: PySide6.QtWidgets.QGraphicsSceneHoverEvent
    ) -> None:
        """
        Restores the mouse cursor when the pointer leaves the shape.
        :param event: The event instance.
        :return: None.
        """
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(
        self, event: PySide6.QtWidgets.QGraphicsSceneMouseEvent
    ) -> None:
        """
        Enable shape resizing when an handle is pressed.
        :param event: The event instance.
        :return: None.
        """
        self.selected_handle = self.handle_at(event.pos())
        if self.selected_handle is not None:
            self.pressed_mouse_pos = event.pos()
            self.pressed_mouse_rect = self.boundingRect()
        super().mousePressEvent(event)

    def mouseMoveEvent(
        self, event: PySide6.QtWidgets.QGraphicsSceneMouseEvent
    ) -> None:
        """
        Resizes the shape.
        :param event:  The event instance.
        :return: None.
        """
        if self.selected_handle is not None:
            self.resize_shape(event.pos())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(
        self, event: PySide6.QtWidgets.QGraphicsSceneMouseEvent
    ) -> None:
        """
        Stops resizing the shape and store the new size.
        :param event: The event instance.
        :return: None.
        """
        super().mouseReleaseEvent(event)
        self.selected_handle = None
        self.pressed_mouse_pos = None
        self.pressed_mouse_rect = None
        self.update()

        # NOTE: command becomes obsolete if the shape is not resized
        command = ResizeShapeCommand(schematic=self.view, selected_shape=self)
        self.view.app.undo_stack.push(command)

    def update_handle_position(self) -> None:
        """
        Updates current resize handles based on the rectangle size and position.
        :return None
        """
        s = self.handle_size
        b = self.boundingRect()
        self.handles[Handles.TOP_LEFT.value] = QRectF(b.left(), b.top(), s, s)
        self.handles[Handles.TOP_MIDDLE.value] = QRectF(
            b.center().x() - s / 2, b.top(), s, s
        )
        self.handles[Handles.TOP_RIGHT.value] = QRectF(
            b.right() - s, b.top(), s, s
        )
        self.handles[Handles.MIDDLE_LEFT.value] = QRectF(
            b.left(), b.center().y() - s / 2, s, s
        )
        self.handles[Handles.MIDDLE_RIGHT.value] = QRectF(
            b.right() - s, b.center().y() - s / 2, s, s
        )
        self.handles[Handles.BOTTOM_LEFT.value] = QRectF(
            b.left(), b.bottom() - s, s, s
        )
        self.handles[Handles.BOTTOM_MIDDLE.value] = QRectF(
            b.center().x() - s / 2, b.bottom() - s, s, s
        )
        self.handles[Handles.BOTTOM_RIGHT.value] = QRectF(
            b.right() - s, b.bottom() - s, s, s
        )

    def handle_at(self, point: QPointF) -> int | None:
        """
        Return the resize handle below the given point.
        :param point: The current point.
        :return The enum of the handle at the point.
        """
        for k, v in self.handles.items():
            if v.contains(point):
                return k
        return None

    def resize_shape(self, pos: QPointF) -> None:
        """
        Resizes the shape on the schematic. This ensures that the rectangle is always
        larger than the prescribed size and the shape is not dragged outside the canvas
        edges.
        :return None.
        """
        offset = self.handle_size + self.handle_space
        bounding_rect = self.boundingRect()
        rect = self.rect()
        diff = QPointF(0, 0)

        self.prepareGeometryChange()
        if self.selected_handle == Handles.TOP_LEFT.value:
            from_x = self.pressed_mouse_rect.left()
            from_y = self.pressed_mouse_rect.top()
            to_x = from_x + pos.x() - self.pressed_mouse_pos.x()
            to_x = self.constraint_left(pos, to_x)
            to_y = from_y + pos.y() - self.pressed_mouse_pos.y()
            to_y = self.constraint_top(pos, to_y)

            diff.setX(to_x - from_x)
            diff.setY(to_y - from_y)
            bounding_rect.setLeft(to_x)
            bounding_rect.setTop(to_y)
            rect.setLeft(bounding_rect.left() + offset)
            rect.setTop(bounding_rect.top() + offset)
            self.setRect(rect)
        elif self.selected_handle == Handles.TOP_MIDDLE.value:
            from_y = self.pressed_mouse_rect.top()
            to_y = from_y + pos.y() - self.pressed_mouse_pos.y()
            to_y = self.constraint_top(pos, to_y)

            diff.setY(to_y - from_y)
            bounding_rect.setTop(to_y)
            rect.setTop(bounding_rect.top() + offset)
            self.setRect(rect)
        elif self.selected_handle == Handles.TOP_RIGHT.value:
            from_x = self.pressed_mouse_rect.right()
            from_y = self.pressed_mouse_rect.top()
            to_x = from_x + pos.x() - self.pressed_mouse_pos.x()
            to_x = self.constraint_right(pos, to_x)
            to_y = from_y + pos.y() - self.pressed_mouse_pos.y()
            to_y = self.constraint_top(pos, to_y)

            diff.setX(to_x - from_x)
            diff.setY(to_y - from_y)
            bounding_rect.setRight(to_x)
            bounding_rect.setTop(to_y)
            rect.setRight(bounding_rect.right() - offset)
            rect.setTop(bounding_rect.top() + offset)
            self.setRect(rect)
        elif self.selected_handle == Handles.MIDDLE_LEFT.value:
            from_x = self.pressed_mouse_rect.left()
            to_x = from_x + pos.x() - self.pressed_mouse_pos.x()
            to_x = self.constraint_left(pos, to_x)

            diff.setX(to_x - from_x)
            bounding_rect.setLeft(to_x)
            rect.setLeft(bounding_rect.left() + offset)
            self.setRect(rect)
        elif self.selected_handle == Handles.MIDDLE_RIGHT.value:
            from_x = self.pressed_mouse_rect.right()
            to_x = from_x + pos.x() - self.pressed_mouse_pos.x()
            to_x = self.constraint_right(pos, to_x)

            diff.setX(to_x - from_x)
            bounding_rect.setRight(to_x)
            rect.setRight(bounding_rect.right() - offset)
            self.setRect(rect)
        elif self.selected_handle == Handles.BOTTOM_LEFT.value:
            from_x = self.pressed_mouse_rect.left()
            from_y = self.pressed_mouse_rect.bottom()
            to_x = from_x + pos.x() - self.pressed_mouse_pos.x()
            to_x = self.constraint_left(pos, to_x)
            to_y = from_y + pos.y() - self.pressed_mouse_pos.y()
            to_y = self.constraint_bottom(pos, to_y)

            diff.setX(to_x - from_x)
            diff.setY(to_y - from_y)
            bounding_rect.setLeft(to_x)
            bounding_rect.setBottom(to_y)
            rect.setLeft(bounding_rect.left() + offset)
            rect.setBottom(bounding_rect.bottom() - offset)
            self.setRect(rect)
        elif self.selected_handle == Handles.BOTTOM_MIDDLE.value:
            from_y = self.pressed_mouse_rect.bottom()
            to_y = from_y + pos.y() - self.pressed_mouse_pos.y()
            to_y = self.constraint_bottom(pos, to_y)

            diff.setY(to_y - from_y)
            bounding_rect.setBottom(to_y)
            rect.setBottom(bounding_rect.bottom() - offset)
            self.setRect(rect)
        elif self.selected_handle == Handles.BOTTOM_RIGHT.value:
            from_x = self.pressed_mouse_rect.right()
            from_y = self.pressed_mouse_rect.bottom()
            to_x = from_x + pos.x() - self.pressed_mouse_pos.x()
            to_x = self.constraint_right(pos, to_x)
            to_y = from_y + pos.y() - self.pressed_mouse_pos.y()
            to_y = self.constraint_bottom(pos, to_y)

            diff.setX(to_x - from_x)
            diff.setY(to_y - from_y)
            bounding_rect.setRight(to_x)
            bounding_rect.setBottom(to_y)
            rect.setRight(bounding_rect.right() - offset)
            rect.setBottom(bounding_rect.bottom() - offset)
            self.setRect(rect)

        self.update_handle_position()

    def constraint_top(self, pos: QPointF, to_y: float) -> float:
        """
        Constraints the rectangle top when it's being resized.
        :param pos: The mouse position from the mouseMoveEvent.
        :param to_y: The position the rectangle side is moved to.
        :return: The updated to_y.
        """
        # rectangle top cannot go outside the top edge of the canvas
        if self.mapToScene(pos.toPoint()).y() + self.handle_space / 2 < 0:
            to_y = self.mapFromScene(0, 0).y()

        # rectangle top cannot be below its bottom
        if to_y + self.min_rect_height >= self.rect().bottom():
            to_y = self.rect().bottom() - self.min_rect_height
        return to_y

    def constraint_bottom(self, pos: QPointF, to_y: float) -> float:
        """
        Constraints the rectangle bottom when it's being resized.
        :param pos: The mouse position from the mouseMoveEvent.
        :param to_y: The position the rectangle side is moved to.
        :return: The updated to_y.
        """
        # rectangle bottom cannot go outside the bottom edge of the canvas
        if (
            self.mapToScene(pos.toPoint()).y() + self.handle_space / 2
            > self.view.schematic_height
        ):
            to_y = self.mapFromScene(0, self.view.schematic_height).y()

        # rectangle bottom cannot be above its top
        if to_y - self.rect().top() <= self.min_rect_height:
            to_y = self.rect().top() + self.min_rect_height

        return to_y

    def constraint_left(self, pos: QPointF, to_x: float) -> float:
        """
        Constraints the rectangle left when it's being resized.
        :param pos: The mouse position from the mouseMoveEvent.
        :param to_x: The position the rectangle side is moved to.
        :return: The updated to_x.
        """
        # rectangle left cannot go outside the left edge of the canvas
        if self.mapToScene(pos.toPoint()).x() + self.handle_space / 2 < 0:
            to_x = self.mapFromScene(0, 0).x()

        # rectangle left cannot be larger than its right
        if to_x + self.min_rect_width >= self.rect().right():
            to_x = self.rect().right() - self.min_rect_width

        return to_x

    def constraint_right(self, pos: QPointF, to_x: float) -> float:
        """
        Constraints the rectangle right when it's being resized.
        :param pos: The mouse position from the mouseMoveEvent.
        :param to_x: The position the rectangle side is moved to.
        :return: The updated to_x.
        """
        # rectangle right cannot go outside the right edge of the canvas
        if (
            self.mapToScene(pos.toPoint()).x() + self.handle_space / 2
            > self.view.schematic_width
        ):
            to_x = self.mapFromScene(self.view.schematic_width, 0).x()

        # rectangle right cannot be smaller than its left
        if to_x - self.rect().left() <= self.min_rect_width:
            to_x = self.rect().left() + self.min_rect_width

        return to_x

    def shape(self) -> PySide6.QtGui.QPainterPath:
        """
        Returns the shape.
        :return: The shape's path.
        """
        path = QPainterPath()
        path.addRect(self.rect())
        if self.isSelected():
            for shape in self.handles.values():
                path.addEllipse(shape)
        return path

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paint the outline when the shape is selected.
        :param painter: The painter instance.
        :param option: The style options.
        :param widget: The widget.
        :return: None
        """
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawRoundedRect(self.rect(), 6, 6)

        # handles
        handle_color = Color("gray", 700).qcolor
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(
            QPen(
                handle_color,
                1.0,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        if self.isSelected():
            [painter.drawRect(handle) for handle in self.handles.values()]

    def contextMenuEvent(
        self, event: PySide6.QtWidgets.QGraphicsSceneContextMenuEvent
    ) -> None:
        """
        Create the context menu.
        :param event: The event being triggered.
        :return: None
        """
        self.view.de_select_all_items()
        self.setSelected(True)

        context_menu = ContextualMenu()
        context_menu.set_title("Rectangle")

        # edit action
        edit_action = context_menu.addAction("Edit style")
        # noinspection PyUnresolvedReferences
        edit_action.triggered.connect(self.on_edit_shape)
        self.view.addAction(edit_action)

        # delete action
        delete_action = context_menu.addAction("Delete shape")
        # noinspection PyUnresolvedReferences
        delete_action.triggered.connect(self.on_delete_item)
        self.view.addAction(delete_action)

        context_menu.exec(event.screenPos())

    @Slot()
    def on_edit_shape(self) -> None:
        """
        Edit a node configuration.
        :return: None
        """
        dialog = ShapeDialog(
            shape_id=self.shape_obj.id,
            form_fields=[
                {
                    "name": "border_size",
                    "default_value": self.shape_obj.default_border_size,
                    "value": self.shape_obj.border_size,
                    "field_type": "integer",
                    "min_value": 1,
                    "max_value": self.shape_obj.max_border_size,
                },
                {
                    "name": "border_color",
                    "field_type": ColorPickerWidget,
                    "default_value": self.shape_obj.default_border_color,
                    "value": self.shape_obj.border_color.toTuple()[0:3],
                },
                {
                    "name": "background_color",
                    "field_type": ColorPickerWidget,
                    "field_args": {"enable_alpha": True},
                    "default_value": self.shape_obj.default_background_color,
                    "value": self.shape_obj.background_color.toTuple(),
                },
            ],
            append_form_items={
                "width": self.shape_obj.width,
                "height": self.shape_obj.height,
            },
            shape_config=self.shape_obj,
            parent=self.view.app,
        )
        # enable save button when a new colour is selected
        for name in ["border_color", "background_color"]:
            color_widget: ColorPickerWidget = dialog.form.find_field_by_name(
                name
            ).widget
            color_widget.changed_color.connect(dialog.form.on_field_changed)
        dialog.show()
