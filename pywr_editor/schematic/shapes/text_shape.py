from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import Slot
from PySide6.QtGui import QFont, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem, QStyle

from pywr_editor.form import ColorPickerWidget, FormValidation
from pywr_editor.model import TextShape
from pywr_editor.style import Color
from pywr_editor.widgets import ContextualMenu

from .base_shape import BaseShape
from .shape_dialogs import ShapeDialog

if TYPE_CHECKING:
    from pywr_editor.schematic import Schematic


class SchematicText(BaseShape, QGraphicsTextItem):
    """
    This widgets renders a text onto the schematic.
    """

    def __init__(self, shape_id: str, shape: TextShape, view: "Schematic"):
        """
        Initialise the text shape.
        :param shape: The TextShape instance.
        :param view: The view where to draw the item.
        """
        BaseShape.__init__(self, shape_id, shape, view)
        QGraphicsTextItem.__init__(self)

        self.view = view
        self.shape_obj = shape
        self.setPlainText(shape.text)

        font = QFont()
        font.setPointSize(shape.font_size)
        self.setFont(font)
        self.adjustSize()
        self.setDefaultTextColor(shape.color)

        # allow interaction
        self.setFlag(
            QGraphicsItem.ItemIsMovable,
            self.view.editor_settings.is_schematic_locked is False,
        )
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        # speed up rendering performance
        self.setCacheMode(QGraphicsItem.ItemCoordinateCache)
        self.setAcceptHoverEvents(False)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        # set position
        self.setPos(shape.x, shape.y)
        self.setZValue(0)

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
        if self.isSelected():
            pen = QPen()
            pen.setColor(Color("red", 500).qcolor)
            painter.setPen(pen)

            line_width = 1
            rect = self.boundingRect()
            rect.setX(rect.x() + line_width)
            rect.setY(rect.y() + line_width)
            rect.setWidth(rect.width() - line_width)
            rect.setHeight(rect.height() - line_width)
            painter.drawRoundedRect(rect, 4, 4)
            # remove default outline
            option.state = QStyle.StateFlag.State_None

        super().paint(painter, option, widget)

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
        context_menu.set_title("Text")

        # edit action
        edit_action = context_menu.addAction("Edit text")
        # noinspection PyUnresolvedReferences
        edit_action.triggered.connect(self.on_edit_shape)
        self.view.addAction(edit_action)

        # delete action
        delete_action = context_menu.addAction("Delete text")
        # noinspection PyUnresolvedReferences
        delete_action.triggered.connect(self.on_delete_shape)
        self.view.addAction(delete_action)

        context_menu.exec(event.screenPos())

    @Slot()
    def on_delete_shape(self) -> None:
        """
        Delete the selected shape.
        :return: None
        """
        self.view.on_delete_item([self])

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
                    "name": "text",
                    "value": self.shape_obj.text,
                    "help_text": "The text to show on the schematic",
                    "validate_fun": self.check_form_text,
                },
                {
                    "name": "font_size",
                    "label": "Text size",
                    "default_value": self.shape_obj.default_font_size,
                    "value": self.shape_obj.font_size,
                    "field_type": "integer",
                    "min_value": self.shape_obj.min_font_size,
                    "max_value": self.shape_obj.max_font_size,
                },
                {
                    "name": "color",
                    "field_type": ColorPickerWidget,
                    "default_value": self.shape_obj.default_font_color,
                    "value": self.shape_obj.color.toTuple()[0:3],
                },
            ],
            shape_dict=self.shape_obj.shape_dict,
            parent=self.view.app,
        )
        # enable save button when a new colour is selected
        color_widget: ColorPickerWidget = dialog.form.find_field_by_name(
            "color"
        ).widget
        color_widget.changed_color.connect(
            lambda: dialog.save_button.setEnabled(True)
        )
        dialog.show()

    def check_form_text(
        self, name: str, label: str, value: str
    ) -> FormValidation:
        """
        Check the text length in the form.
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The FormValidation instance.
        """
        if len(value) < self.shape_obj.min_text_size:
            return FormValidation(
                validation=False,
                error_message="The text must be at least "
                + f"{self.shape_obj.min_text_size} characters long",
            )

        return FormValidation(validation=True)
