from enum import Enum
from math import atan2, cos, pi, sin
from typing import TYPE_CHECKING, Union

import PySide6
from PySide6.QtCore import QLineF, QPointF, QRectF, Slot
from PySide6.QtGui import QPainter, QPainterPath, QPen, QPolygonF, Qt
from PySide6.QtWidgets import QGraphicsItem, QGraphicsLineItem

from pywr_editor.form import ColorPickerWidget
from pywr_editor.model import LineArrowShape
from pywr_editor.style import Color
from pywr_editor.widgets import ContextualMenu

from ..commands.resize_shape_command import ResizeShapeCommand
from .abstract_schematic_shape import AbstractSchematicShape
from .shape_dialogs import ShapeDialog

if TYPE_CHECKING:
    from pywr_editor.schematic import Schematic


class Handles(Enum):
    SOURCE_POINT = 0
    TARGET_POINT = 1


class SchematicArrow(AbstractSchematicShape, QGraphicsLineItem):
    """
    This widgets renders a line arrow onto the schematic.
    """

    handle_size = 8
    """ The size of the handle """
    handle_space = -4
    """ Reduce the handle interactive area by the provided space """
    min_line_length = 50
    """ The minimum length of the line """

    def __init__(self, shape_id: str, shape: LineArrowShape, view: "Schematic"):
        """
        Initialise the line arrow shape.
        :param shape: The LineArrowShape instance.
        :param view: The view where to draw the item.
        """
        AbstractSchematicShape.__init__(self, shape_id, shape, view)
        QGraphicsLineItem.__init__(self)

        self.view = view
        self.shape_obj = shape
        self.handles: dict[int, QRectF] = {}
        self.selected_handle = None
        self.pressed_mouse_pos = None

        # shape style for the paint method
        self.pen = QPen(shape.border_color)
        self.pen.setWidth(shape.border_size)

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

        # set positions
        self.setPos(shape.x, shape.y)
        self.setLine(QLineF.fromPolar(shape.length, shape.angle))
        self.setZValue(-1)  # place it behind all items

        # store the position after drawing the item
        self.prev_position = self.scenePos().toTuple()
        self.update_handle_position()

    def hoverMoveEvent(self, event: PySide6.QtWidgets.QGraphicsSceneHoverEvent) -> None:
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
                else Qt.CursorShape.SizeHorCursor
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

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: PySide6.QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Resizes the shape.
        :param event: The event instance.
        :return: None.
        """
        if self.selected_handle is not None:
            self.rotate_shape(event.pos())
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            super().mouseMoveEvent(event)
            self.setCursor(Qt.CursorShape.ArrowCursor)

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
        self.update()

        command = ResizeShapeCommand(schematic=self.view, selected_shape=self)
        self.view.app.undo_stack.push(command)

    def update_handle_position(self) -> None:
        """
        Updates current resize handles based on the rectangle size and position.
        :return None
        """
        sp = self.line().p1()
        tp = self.line().p2()
        s = self.handle_size

        self.handles[Handles.SOURCE_POINT.value] = QRectF(
            sp.x() - s / 2, sp.y() - s / 2, s, s
        )
        self.handles[Handles.TARGET_POINT.value] = QRectF(
            tp.x() - s / 2, tp.y() - s / 2, s, s
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

    def rotate_shape(self, pos: QPointF) -> None:
        """
        Rotates the shape on the schematic by moving its source and target point.
        The line is not updated if its length is less than the minium allowed length.
        :return None.
        """
        self.prepareGeometryChange()

        line = None
        if self.selected_handle == Handles.SOURCE_POINT.value:
            pos = self.constraint_point(pos)
            line = QLineF(pos, self.line().p2())
        elif self.selected_handle == Handles.TARGET_POINT.value:
            pos = self.constraint_point(pos)
            line = QLineF(self.line().p1(), pos)

        if line:
            # ensure that the line has a minimum length
            if line.length() < self.min_line_length:
                line.setLength(self.min_line_length)

            self.setLine(line)

        # if the line position/length is adjusted make sure it stays in the canvas
        self.adjust_position()

        self.update_handle_position()

    def constraint_point(self, moved_point: QPointF) -> QPointF:
        """
        Constraints the moved point to make sure the moved shape stays within the
        canvas boundaries.
        :param moved_point: The line point being moved.
        :return: The new coordinates of the moved point.
        """
        scene_moved_point = self.mapToScene(moved_point)
        if scene_moved_point.x() <= 0:
            scene_moved_point.setX(self.handle_size)
        if scene_moved_point.x() >= self.view.schematic_width:
            scene_moved_point.setX(self.view.schematic_width - self.handle_size)
        if scene_moved_point.y() <= 0:
            scene_moved_point.setY(self.handle_size)
        if scene_moved_point.y() >= self.view.schematic_height:
            scene_moved_point.setY(self.view.schematic_height - self.handle_size)

        return self.mapFromScene(scene_moved_point)

    def get_shape_boundary_points(
        self,
        handle: Union[Handles.SOURCE_POINT.name, Handles.TARGET_POINT.name],
    ) -> [QPointF, QPointF]:
        """
        Returns the shape boundary points that include the provided handle. This
        accounts for the line angle.
        :param handle: The handle type.
        :return: The shape boundary points wrapping around the handle in clockwise
        order.
        """
        # counter-clockwise angle from positive x-axis direction. The angle
        # indicates where the arrow points to (to p2)
        angle_deg = self.line().angle()
        angle = angle_deg * 0.0174533
        b = self.handle_size
        h = self.handles[handle.value]

        # flip quadrant if point is P2
        if handle == Handles.TARGET_POINT:
            angle = angle + pi
        # correct angle when adjusted
        if angle > 2 * pi:
            angle = 2 * pi - angle
        if angle < 0:
            angle = abs(angle)

        # angle=[270; 360] P1 in 2nd quadrant, P2 in 4th quadrant
        if 3 / 2 * pi <= angle < 2 * pi:
            point1 = QPointF(
                h.left() - b * sin(pi - angle) * cos(pi - angle),
                h.bottom() - b * sin(pi - angle) * sin(pi - angle),
            )
            point2 = QPointF(
                h.left() + b * sin(pi - angle) * sin(pi - angle),
                h.bottom() - b - b * sin(pi - angle) * cos(pi - angle),
            )
        # angle=[180; 270] P1 in 1st quadrant, P2 in 3rd quadrant
        elif pi <= angle < 3 / 2 * pi:
            point1 = QPointF(
                h.left() + b * cos(angle) * cos(angle),
                h.bottom() - b - b * cos(angle) * sin(angle),
            )
            point2 = QPointF(
                h.left() + b + b * cos(pi / 2 - angle) * sin(pi / 2 - angle),
                h.bottom() - b * cos(pi / 2 - angle) * cos(pi / 2 - angle),
            )
        # angle=[90; 180] P1 in 4th quadrant, P2 in 2nd quadrant
        elif pi / 2 <= angle < pi:
            point1 = QPointF(
                h.left() + b + b * cos(angle - pi / 2) * sin(angle - pi / 2),
                h.bottom() - b + b * cos(angle - pi / 2) * cos(angle - pi / 2),
            )
            point2 = QPointF(
                h.left() + b * cos(pi - angle) * cos(pi - angle),
                h.bottom() + b * cos(pi - angle) * sin(pi - angle),
            )
        # angle=[0; 90] P1 in 3rd quadrant, P2 in 1st quadrant
        else:
            point1 = QPointF(
                h.left() + b - b * cos(angle) * cos(angle),
                h.bottom() + b * cos(angle) * sin(angle),
            )
            point2 = QPointF(
                h.left() - b * cos(pi / 2 - angle) * sin(pi / 2 - angle),
                h.bottom() - b + b * cos(pi / 2 - angle) * cos(pi / 2 - angle),
            )

        if handle == Handles.TARGET_POINT:
            return point2, point1
        return point1, point2

    def shape(self) -> PySide6.QtGui.QPainterPath:
        """
        Returns the shape including the handles' areas. The shape is changed to make
        the sensitive area larger, so that it is easier to move or resize the line
        arrow.
        :return: The shape's path.
        """
        if not self.handles:
            return QPainterPath()

        source_p1, source_p2 = self.get_shape_boundary_points(Handles.SOURCE_POINT)
        target_p1, target_p2 = self.get_shape_boundary_points(Handles.TARGET_POINT)
        path = QPainterPath()
        path.moveTo(source_p1)
        path.lineTo(source_p2)
        path.lineTo(target_p2)
        path.lineTo(target_p1)
        path.lineTo(source_p1)

        return path

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: PySide6.QtWidgets.QWidget | None = ...,
    ) -> None:
        """
        Paint the arrow head and the outline when the shape is selected.
        :param painter: The painter instance.
        :param option: The style options.
        :param widget: The widget.
        :return: None
        """
        arrow_size = 7

        # draw the edge and line
        painter.setPen(
            QPen(
                self.pen.color(),
                self.pen.width(),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.drawLine(self.line())

        angle = atan2(-self.line().dy(), self.line().dx())
        target_point = self.line().p2()
        target_arrow_p1 = target_point + QPointF(
            sin(angle - pi / 3) * arrow_size,
            cos(angle - pi / 3) * arrow_size,
        )
        target_arrow_p2 = target_point + QPointF(
            sin(angle - pi + pi / 3) * arrow_size,
            cos(angle - pi + pi / 3) * arrow_size,
        )

        painter.setBrush(self.pen.color())
        pol = QPolygonF()
        pol.append(target_point)
        pol.append(target_arrow_p1)
        pol.append(target_arrow_p2)
        painter.drawPolygon(pol)

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

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(Color("gray", 300).qcolor)
            painter.drawPath(self.shape())

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
        context_menu.set_title("Arrow")

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
            ],
            append_form_items={
                "length": self.shape_obj.length,
                "angle": self.shape_obj.angle,
            },
            shape_config=self.shape_obj,
            parent=self.view.app,
        )

        # enable save button when a new colour is selected
        color_widget: ColorPickerWidget = dialog.form.find_field_by_name(
            "border_color"
        ).widget
        color_widget.changed_color.connect(dialog.form.on_field_changed)
        dialog.show()
