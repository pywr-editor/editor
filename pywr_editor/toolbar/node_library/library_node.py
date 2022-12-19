import PySide6
import pywr_editor
import pywr_editor.node_shapes
from typing import TYPE_CHECKING
from PySide6.QtGui import QPixmap, Qt, QPainter
from PySide6.QtWidgets import (
    QGraphicsItem,
    QStyleOptionGraphicsItem,
    QGraphicsItemGroup,
)
from .library_node_label import LibraryNodeLabel

if TYPE_CHECKING:
    from .nodes_library import NodesLibraryPanel
    from pywr_editor.schematic import SchematicItem


class LibraryNode(QGraphicsItemGroup):
    max_label_size = 25
    not_import_custom_node_name = "Custom node"

    def __init__(
        self, view: "NodesLibraryPanel", node_class_type: str, node_name: str
    ):
        """
        Initialises the class.
        :param view: The view where to draw the item.
        :param node_class_type: The name of the node class.
        :param node_name: The name of the node to show under the node's shape.
        :return None
        """
        super().__init__()
        self.node_class_type = node_class_type
        self.node_name = node_name
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

        # node icon
        try:
            node_class = getattr(pywr_editor.node_shapes, node_class_type)
        except AttributeError:
            # node name is not a built-in component
            node_class = getattr(pywr_editor.node_shapes, "CustomNodeShape")
        self.node: "SchematicItem" = node_class(parent=self)

        # label
        self.label = LibraryNodeLabel(
            parent=self,
            name=self.name,
            color=self.node.label,
        )

        # add elements to the group
        self.addToGroup(self.node)
        self.addToGroup(self.label)

    def setPos(self, pos: PySide6.QtCore.QPointF) -> None:
        """
        Sets the position of the node.
        :param pos: The node Position as QPointF instance.
        :return: None
        """
        self.x = pos.x()
        self.y = pos.y()
        super().setPos(pos)

    @property
    def name(self) -> str:
        """
        Gets the trimmed node name.
        :return: The formatted name.
        """
        label = self.node_name

        if len(label) > self.max_label_size:
            label = f"{label[0:self.max_label_size]}..."

        return label

    def pixmap_from_item(self) -> QPixmap:
        """
        Converts the node to a pixmap instance.
        :return: The QPixmap instance.
        """
        item = self.node

        pixmap = QPixmap(item.boundingRect().size().toSize())
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.scale(0.8, 0.8)
        painter.translate(-item.boundingRect().x(), -item.boundingRect().y())
        painter.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform
        )

        options = QStyleOptionGraphicsItem()
        item.paint(painter, options)
        # render children
        children = item.childItems()
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
        self.node.hover = True
        self.node.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(
        self, event: PySide6.QtWidgets.QGraphicsSceneHoverEvent
    ) -> None:
        """
        Sets the hover status to False for the shape.
        :param event: The event being triggered.
        :return: None
        """
        self.node.hover = False
        self.node.update()
        super().hoverLeaveEvent(event)
