from typing import TYPE_CHECKING, Type

import PySide6
from PySide6.QtGui import QPainter, QPixmap, Qt
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsItemGroup,
    QStyleOptionGraphicsItem,
)

from pywr_editor.style import Color

from .library_item_label import LibraryItemLabel

if TYPE_CHECKING:
    from .schematic_items_library import LibraryPanel


class LibraryItem(QGraphicsItemGroup):
    """
    Class that draws the library item.
    """

    max_label_size = 25
    """ The maximum size of the label to display beneath the item. """
    not_import_custom_node_name = "Custom node"
    """ The label for nodes that were not imported. """

    def __init__(
        self,
        view: "LibraryPanel",
        item_class_type: Type[QGraphicsItem | QGraphicsItemGroup],
        name: str,
        node_type: str | None = None,
    ):
        """
        Initialise the class.
        :param view: The view where to draw the item.
        :param item_class_type: The name of the graphical node or shape class.
        :param name: The name of the node or shape to show under the graphical item.
        :param node_type: For nodes, the pywr node type.
        :return None
        """
        super().__init__()
        self.item_class_type = item_class_type
        self.name = name
        self.node_type = node_type

        self.view = view
        self.x: float = 0
        self.y: float = 0

        # disallow interaction
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        # speed up rendering performance
        self.setCacheMode(QGraphicsItem.ItemCoordinateCache)
        # enable hover event
        self.setAcceptHoverEvents(True)

        self.item = item_class_type(parent=self)
        try:
            # label from node's colour
            label_color = self.item.label
        except AttributeError:
            # for shapes
            label_color = Color("gray", 800)

        # label
        self.label = LibraryItemLabel(
            parent=self,
            name=self.trimmed_name,
            color=label_color,
        )

        # add elements to the group
        self.addToGroup(self.item)
        self.addToGroup(self.label)

    def setPos(self, pos: PySide6.QtCore.QPointF) -> None:
        """
        Set the position of the item.
        :param pos: The item position as QPointF instance.
        :return: None
        """
        self.x = pos.x()
        self.y = pos.y()
        super().setPos(pos)

    @property
    def trimmed_name(self) -> str:
        """
        Gets the trimmed item's name.
        :return: The formatted name.
        """
        label = self.name

        if len(label) > self.max_label_size:
            label = f"{label[0:self.max_label_size]}..."

        return label

    def pixmap_from_item(self) -> QPixmap:
        """
        Converts the item to a pixmap instance.
        :return: The QPixmap instance.
        """
        pixmap = QPixmap(self.item.boundingRect().size().toSize())
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.scale(0.8, 0.8)
        painter.translate(
            -self.item.boundingRect().x(), -self.item.boundingRect().y()
        )
        painter.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform
        )

        options = QStyleOptionGraphicsItem()
        self.item.paint(painter, options, None)
        # render children
        children = self.item.childItems()
        if len(children) > 0:
            for child in children:
                child.paint(painter, options)

        return pixmap

    def hoverEnterEvent(
        self, event: PySide6.QtWidgets.QGraphicsSceneHoverEvent
    ) -> None:
        """
        Sets the hover status to True for the shape.
        :param event: The event being triggered.
        :return: None
        """
        self.item.hover = True
        self.item.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(
        self, event: PySide6.QtWidgets.QGraphicsSceneHoverEvent
    ) -> None:
        """
        Sets the hover status to False for the shape.
        :param event: The event being triggered.
        :return: None
        """
        self.item.hover = False
        self.item.update()
        super().hoverLeaveEvent(event)
