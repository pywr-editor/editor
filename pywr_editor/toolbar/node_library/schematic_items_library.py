from functools import partial
from typing import TYPE_CHECKING, Literal

import PySide6
from PySide6.QtCore import QMimeData, QPointF, QSize, Slot
from PySide6.QtGui import QDrag, QFont, QPainter, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import pywr_editor
import pywr_editor.node_shapes
from pywr_editor.style import Color, stylesheet_dict_to_str
from pywr_editor.widgets import PushIconButton

from .library_item import LibraryItem
from .library_shapes import ArrowShape, BaseShape, RectangleShape, TextShape

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class SchematicItemsLibrary(QWidget):
    def __init__(self, parent: "MainWindow"):
        """
        Initialise the items' library.
        :param parent: The parent widget.
        """
        super().__init__()

        self.window = parent
        self.panel = LibraryPanel(self)

        # Scroll buttons
        self.scroll_up = PushIconButton(
            icon=":toolbar/scroll-up", icon_size=QSize(10, 10)
        )
        self.scroll_up.setStyleSheet(self.button_stylesheet("up"))
        self.scroll_up.setEnabled(False)
        # noinspection PyUnresolvedReferences
        self.scroll_up.clicked.connect(partial(self.on_scroll, "up"))

        self.scroll_down = PushIconButton(
            icon=":toolbar/scroll-down", icon_size=QSize(10, 10)
        )
        self.scroll_down.setStyleSheet(self.button_stylesheet("down"))
        # noinspection PyUnresolvedReferences
        self.scroll_down.clicked.connect(partial(self.on_scroll, "down"))

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.scroll_up)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.scroll_down)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.panel)
        layout.addLayout(buttons_layout)

    @Slot()
    def on_scroll(self, direction: Literal["up", "down"]) -> None:
        """
        Scrolls the panel after pressing the scroll up or down button.
        :param direction: The direction of scroll ("up" or "down").
        :return: None
        """
        delta = 26 if direction == "down" else -26
        self.panel.verticalScrollBar().setValue(
            self.panel.verticalScrollBar().value() + delta
        )
        self.toggle_scroll_buttons()

    def toggle_scroll_buttons(self) -> None:
        """
        Enables/disables the scroll buttons when the scrollbar reaches the top or
        bottom of the scroll area.
        :return: None
        """
        if (
            self.panel.verticalScrollBar().value()
            == self.panel.verticalScrollBar().maximum()
        ):
            self.scroll_down.setEnabled(False)
            self.scroll_up.setEnabled(True)
        elif (
            self.panel.verticalScrollBar().value()
            == self.panel.verticalScrollBar().minimum()
        ):
            self.scroll_down.setEnabled(True)
            self.scroll_up.setEnabled(False)
        else:
            self.scroll_down.setEnabled(True)
            self.scroll_up.setEnabled(True)

    @staticmethod
    def button_stylesheet(button: Literal["up", "down"]) -> str:
        """
        Returns the button stylesheet as string.
        :param button: The button the style is applied to ("up" or "down).
        :return: The style sheet.
        """
        style_dict = {
            "PushIconButton": {
                "border": f"1px solid {Color('gray', 300).hex}",
                "border-radius": "4px",
                "padding": "0px 1px",
                "margin-top": 0,
                ":disabled": {
                    "background": "rgba(0, 0, 0, 5)",
                    "border": "1px solid rgba(0, 0, 0, 5)",
                    "color": "rgba(0, 0, 0, 80)",
                },
            },
        }
        # use same margin from panel
        if button == "up":
            # noinspection PyTypedDict
            style_dict["PushIconButton"]["margin-top"] = "6px"

        return stylesheet_dict_to_str(style_dict)


class LibraryPanel(QGraphicsView):
    view_scale = 0.75
    """ The default scaling factor. """
    shapes = {
        "Text box": TextShape,
        "Rectangle": RectangleShape,
        "Arrow": ArrowShape,
    }
    """ Dictionary with the shape labels and classes. """

    def __init__(self, parent: SchematicItemsLibrary):
        """
        :return: None
        """
        super().__init__()
        self.container = parent
        self.window = parent.window
        self.init = False
        self.node_dict = {}

        # built-in nodes
        self.built_in_node_dict = {
            item["class"]: item["name"]
            for node_type, item in self.window.model_config.pywr_node_data.nodes_data.items()  # noqa: E501
        }
        # store available nodes for the first time
        self.update_available_nodes()

        # behaviour
        self.setFixedHeight(90)
        self.setMinimumWidth(600)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setToolTip(
            "Add a new item by dragging and dropping it onto the schematic"
        )

        # appearance
        self.setRenderHints(
            QPainter.Antialiasing
            | QPainter.SmoothPixmapTransform
            | QPainter.TextAntialiasing
        )
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(self.stylesheet)

        # draw the scene
        self.scene = QGraphicsScene(parent=self)
        self.setScene(self.scene)
        self.add_items()
        self.init = True

    def update_available_nodes(self) -> None:
        """
        Adds or updates the list of custom nodes available in the panel.
        :return: None
        """
        self.node_dict = self.built_in_node_dict.copy()

        # add custom imported nodes and the generic custom node to let user add
        # not-imported custom nodes to the schematic
        self.node_dict = {
            **self.node_dict,
            **{
                item["name"]: item["name"]
                for item in self.window.model_config.includes.get_custom_nodes().values()  # noqa: E501
            },
            "CustomNode": LibraryItem.not_import_custom_node_name,
        }

    def draw_section_title(self, text: str, position: list[float]) -> None:
        """
        Draw a section title.
        :param text: The text.
        :param position: The title position.
        :return: None
        """
        title = QGraphicsTextItem(text)
        font = QFont()
        font.setPixelSize(16)
        font.setBold(True)
        title.setFont(font)
        title.setPos(QPointF(*position))
        title.setDefaultTextColor(Color("gray", 700).qcolor)
        self.scene.addItem(title)

    def add_items(self) -> None:
        """
        Adds the nodes and the shapes to the scene widget.
        :return: None
        """
        self.draw_section_title("Nodes", [-5, -15])

        # position nodes on the dummy schematic
        x0 = 10
        y = 35
        x = x0
        for ni, (node_type, node_name) in enumerate(self.node_dict.items()):
            # node icon
            try:
                node_class_type = getattr(pywr_editor.node_shapes, node_type)
            except AttributeError:
                # node name is not a built-in component
                node_class_type = getattr(pywr_editor.node_shapes, "CustomNode")
            node_obj = LibraryItem(
                view=self,
                item_class_type=node_class_type,
                name=node_name,
                node_type=node_type,
            )
            self.scene.addItem(node_obj)

            if ni != 0:
                x += 220
            if x >= self.width() - 10:
                x = x0
                y += 35
            node_obj.setPos(QPointF(x, y))

        self.draw_section_title("Shapes", [-5, y + 25])
        y += 35
        # position shapes
        for name, shape_type in self.shapes.items():
            shape_obj = LibraryItem(
                view=self, item_class_type=shape_type, name=name
            )
            self.scene.addItem(shape_obj)
            x += 220
            if x >= self.width() - 10:
                x = x0
                y += 35
            shape_obj.setPos(QPointF(x, y))

        self.setSceneRect(-20, -20, self.width(), y + 35)
        if not self.init:
            self.scale(self.view_scale, self.view_scale)

    def reload(self) -> None:
        """
        Updates the library.
        :return: None
        """
        self.scene.clear()
        self.update_available_nodes()
        self.add_items()

    def wheelEvent(self, event: PySide6.QtGui.QWheelEvent) -> None:
        """
        Handles zoom using the mouse wheel.
        :param event: The event being triggered.
        :return: None
        """
        # make scroll smoother
        delta = 4
        if event.angleDelta().y() > 0:
            scroll_delta = -delta
        else:
            scroll_delta = delta
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().value() + scroll_delta
        )
        # toggle scroll buttons
        self.parent().toggle_scroll_buttons()

    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        """
        Handles the mouse press event to initialise the drag action.
        :param event: The event being triggered.
        :return: None
        """
        items = self.items(event.pos())
        items = [i for i in items if isinstance(i, LibraryItem)]
        if len(items) == 0:
            return

        lib_item = items[0]
        mime_data = QMimeData()
        # set the shape type
        if isinstance(lib_item.item, BaseShape):
            mime_data.setText(f"Shape.{lib_item.item.__class__.__name__}")
        # set the node class name
        else:
            mime_data.setText(lib_item.node_type)

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        drag.setPixmap(lib_item.pixmap_from_item())
        drag.exec()

    def dragMoveEvent(self, event: PySide6.QtGui.QDragMoveEvent) -> None:
        """
        Accepts the drag action.
        :param event: The action being triggered.
        :return: None
        """
        if event.mimeData().hasText():
            event.accept()

    @property
    def stylesheet(self):
        """
        Returns the widget stylesheet as string
        :return: The style sheet.
        """
        return stylesheet_dict_to_str(
            {
                "LibraryPanel": {
                    # explicitly set background to properly set border radius
                    "background-color": "palette(base)",
                    "border": f"1px solid {Color('gray', 300).hex}",
                    "border-radius": "4px",
                    "margin-top": "5px",
                },
            },
        )
