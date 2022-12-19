import PySide6
from typing import Literal, TYPE_CHECKING
from functools import partial
from PySide6.QtCore import QPointF, QMimeData, Slot, QSize
from PySide6.QtGui import QPainter, Qt, QDrag
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QFrame,
    QSizePolicy,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)
from .library_node import LibraryNode
from pywr_editor.style import Color, stylesheet_dict_to_str
from pywr_editor.widgets import PushIconButton
from pywr_editor.model import ModelConfig

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class NodesLibrary(QWidget):
    def __init__(self, parent: "MainWindow"):
        """
        Initialises the node's library.
        :param parent: The parent widget.
        """
        super().__init__()

        self.window = parent
        self.panel = NodesLibraryPanel(self)

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
        delta = 30 if direction == "down" else -30
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


class NodesLibraryPanel(QGraphicsView):
    view_scale = 0.75

    def __init__(self, parent: NodesLibrary):
        """
        :return: None
        """
        super().__init__()
        self.container = parent
        self.window = parent.window

        # built-in nodes
        self.node_dict = {
            item["class"]: item["name"]
            for node_type, item in self.window.model_config.pywr_node_data.nodes_data.items()  # noqa: E501
        }
        # add custom imported nodes and the generic custom node to let user add
        # not-imported custom nodes to the schematic
        self.node_dict = {
            **self.node_dict,
            **{
                item["name"]: item["name"]
                for item in self.window.model_config.includes.get_custom_nodes().values()  # noqa: E501
            },
            LibraryNode.not_import_custom_node_name: LibraryNode.not_import_custom_node_name,  # noqa: E501
        }

        # behaviour
        self.setFixedHeight(90)
        self.setMinimumWidth(700)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setToolTip(
            "Add a new node by dragging and dropping it onto the schematic"
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
        self.add_nodes()

    @staticmethod
    def get_available_nodes(model_config: ModelConfig) -> dict[str, str]:
        """
        Returns a dictionary containing the available nodes in the library.
        :param model_config: The ModelConfig instance.
        :return: A dictionary with the node class name as key and the node's name
        as value.
        """
        # built-in nodes
        node_dict = {
            item["class"]: item["name"]
            for node_type, item in model_config.pywr_node_data.nodes_data.items()
        }
        # add custom imported nodes and the generic custom node to let user add
        # not-imported custom nodes to the schematic
        node_dict = {
            **node_dict,
            **{
                item["name"]: item["name"]
                for item in model_config.includes.get_custom_nodes().values()
            },
            "CustomNode": LibraryNode.not_import_custom_node_name,
        }

        return node_dict

    def add_nodes(self) -> None:
        """
        Adds the node to the scene widget.
        :return: None
        """
        # position nodes on the dummy schematic
        x0 = 10
        y = 0
        x = x0
        for ni, (node_type, node_name) in enumerate(
            self.get_available_nodes(self.window.model_config).items()
        ):
            node_obj = LibraryNode(
                view=self, node_class_type=node_type, node_name=node_name
            )
            self.scene.addItem(node_obj)

            if ni != 0:
                x += 220
            if x >= self.width() - 10:
                x = x0
                y += 35
            node_obj.setPos(QPointF(x, y))

        self.scale(self.view_scale, self.view_scale)
        self.setSceneRect(-20, -20, self.width(), y + 35)

    def wheelEvent(self, event: PySide6.QtGui.QWheelEvent) -> None:
        """
        Handles zoom using the mouse wheel.
        :param event: The event being triggered.
        :return: None
        """
        # make scroll smoother
        delta = 2
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
        nodes = self.items(event.pos())
        nodes = [node for node in nodes if isinstance(node, LibraryNode)]
        if len(nodes) == 0:
            return
        node = nodes[0]
        mime_data = QMimeData()
        mime_data.setText(node.node_class_type)

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        drag.setPixmap(node.pixmap_from_item())
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
                "NodesLibraryPanel": {
                    "border": f"1px solid {Color('gray', 300).hex}",
                    "border-radius": "4px",
                    "margin-top": "6px",
                },
            },
        )
