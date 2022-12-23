from typing import Type

import shiboken6
from PySide6.QtCore import QSize
from PySide6.QtGui import QPainter, QPixmap, Qt
from PySide6.QtWidgets import QGraphicsItemGroup, QStyleOptionGraphicsItem

import pywr_editor.node_shapes as all_nodes
from pywr_editor.model import NodeConfig

from .base_node import BaseNode
from .custom_node_shape import CustomNodeShape
from .pywr.pywr_node import PywrNode


def get_node_icon_classes(include_pywr_nodes: bool = True) -> list[str]:
    """
    Returns a list of class types used to style the node.
    :param include_pywr_nodes: Whether to include the styles of the built-in
    pywr nodes. Default to True.
    :return: The list of class types for the node icons.
    """
    node_to_exclude = [
        "BaseNode",
        "BaseReservoir",
        "SvgIcon",
        "Circle",
        "CustomNodeShape",
    ]
    if not include_pywr_nodes:
        node_to_exclude += [
            module
            for module in dir(all_nodes)
            if isinstance(
                getattr(all_nodes, module),
                shiboken6.Object.__class__,
            )
            and issubclass(getattr(all_nodes, module), PywrNode)
        ]

    return [
        module
        for module in dir(all_nodes)
        if module not in node_to_exclude
        and isinstance(getattr(all_nodes, module), shiboken6.Object.__class__)
        and issubclass(getattr(all_nodes, module), BaseNode)
    ]


def get_node_icon(
    model_node_obj: NodeConfig, ignore_custom_type: bool = False
) -> Type[BaseNode] | None:
    """
    Returns the node shape type from the model node type.
    :param model_node_obj: The NodeConfig instance.
    :param ignore_custom_type: When True, it ignores the custom icon if set.
    :return: The shape instance if found, None otherwise.
    """
    node_type = model_node_obj.type
    custom_node_style = model_node_obj.custom_style

    available_classes = get_node_icon_classes()
    lowercase_classes = [name.lower() for name in available_classes]
    # return custom style first
    if (
        custom_node_style is not None
        and custom_node_style in lowercase_classes
        and not ignore_custom_type
    ):
        pos = lowercase_classes.index(custom_node_style)
        return getattr(all_nodes, available_classes[pos])

    # node style from type
    if node_type in lowercase_classes:
        pos = lowercase_classes.index(node_type)
        return getattr(all_nodes, available_classes[pos])
    # custom node
    else:
        return CustomNodeShape


class DummyGraphicsItem(QGraphicsItemGroup):
    def __init__(self, node_class: Type[BaseNode]):
        """
        Dummy class to make use of schematic icons.
        :param node_class: The node class type.
        """
        super().__init__()
        self.node: BaseNode = node_class(parent=self)


def get_pixmap_from_type(
    size: QSize, icon_class_type: Type[BaseNode]
) -> [QPixmap, str]:
    """
    Converts the node icon to a pixmap instance.
    :param size: The QSize of the icon to paint.
    :param icon_class_type: The class type of the schematic icon.
    :return: The QPixmap instance and the name of the icon.
    """
    item = DummyGraphicsItem(icon_class_type)
    icon_class = item.node

    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.translate(
        -icon_class.boundingRect().x(), -icon_class.boundingRect().y()
    )
    painter.setRenderHints(
        QPainter.Antialiasing | QPainter.SmoothPixmapTransform
    )

    options = QStyleOptionGraphicsItem()
    icon_class.paint(painter, options, None)
    # render children
    children = icon_class.childItems()
    if len(children) > 0:
        for child in children:
            child.paint(painter, options)

    return pixmap, icon_class.name
