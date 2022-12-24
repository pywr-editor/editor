from typing import TYPE_CHECKING, Sequence, Union

import PySide6
from PySide6 import QtGui
from PySide6.QtCore import QPointF, QRectF, Qt, QUuid, Signal, Slot
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsView,
    QPushButton,
    QVBoxLayout,
)

from pywr_editor.model import Edges, ModelConfig, NodeConfig
from pywr_editor.node_shapes import get_node_icon_classes
from pywr_editor.schematic import (
    AddNodeCommand,
    ConnectNodeCommand,
    DeleteNodeCommand,
    MoveNodeCommand,
    SchematicBBoxUtils,
    SchematicItem,
    scaling_factor,
    units_to_factor,
)
from pywr_editor.style import Color, stylesheet_dict_to_str
from pywr_editor.toolbar import NodesLibraryPanel

from .connecting_node_props import ConnectingNodeProps
from .edge import Edge, TempEdge
from .schematic_canvas import SchematicCanvas

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class Schematic(QGraphicsView):
    padding: int = 50
    """ canvas padding """
    pywr_bounds: tuple[int] = (-100, 100)
    """ bounds used in the pixels conversion """
    max_view_size_delta: int = 50
    """ max step increment to use when resizing the schematic """
    schematic_move_event = Signal(QPointF)
    """ event emitted when schematic is moved """
    connect_node_event = Signal(SchematicItem)
    """ event emitted when a node is being connected to another """
    min_zoom = scaling_factor("zoom-out", 3)
    """ min zoom factor"""
    max_zoom = scaling_factor("zoom-in", 3)
    """ max zoom factor"""

    def __init__(self, model_config: ModelConfig, app: "MainWindow"):
        """
        :param model_config: The instance representing the model dictionary.
        :param app: The application.
        :return: None
        """
        super().__init__(app)
        self.init = True
        self.model_config = model_config
        self.app = app
        self.editor_settings = self.app.editor_settings
        self.canvas_drag = False

        # initialises the schematic view
        schematic_size = model_config.schematic_size
        self.schematic_width = schematic_size[0]
        self.schematic_height = schematic_size[1]
        self.scaling_factor = self.editor_settings.zoom_level
        self.nodes_wo_position = 0
        self.connecting_node_props = ConnectingNodeProps()
        self.schematic_items: dict[str, SchematicItem] = {}

        # noinspection PyUnresolvedReferences
        self.schematic_move_event.connect(self.on_schematic_move)
        # noinspection PyUnresolvedReferences
        self.connect_node_event.connect(self.on_connect_node_end)
        self.node_classes = get_node_icon_classes()

        # behaviour
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate
        )
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAcceptDrops(True)

        # appearance
        self.setRenderHints(
            QPainter.Antialiasing
            | QPainter.SmoothPixmapTransform
            | QPainter.TextAntialiasing
        )
        self.update_scene_size()
        self.setAlignment(Qt.AlignCenter)

        # draw the scene
        self.scene = QGraphicsScene(parent=self)
        # noinspection PyUnresolvedReferences
        self.scene.changed.connect(self.on_scene_change)
        # noinspection PyUnresolvedReferences
        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.setScene(self.scene)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # add the canvas
        self.canvas = None
        self.add_scene_decorations()

        # adjust the view
        self.scale(self.scaling_factor, self.scaling_factor)
        center = self.app.editor_settings.schematic_center
        if center is not None:
            self.centerOn(center)

        # add top button
        self.abort_node_connection_button = None
        self.add_abort_node_connection_button()

    def add_scene_decorations(self) -> None:
        """
        Adds the canvas border and background to the scene.
        :return: None
        """
        self.scene.setBackgroundBrush(Color("gray", 300).qcolor)
        # add the canvas
        self.canvas = SchematicCanvas(
            width=self.schematic_width, height=self.schematic_height
        )
        self.scene.addItem(self.canvas)

    def draw(self) -> None:
        """
        Draws the schematic.
        :return: None
        """
        # draw the nodes
        for node_index, node_props in enumerate(
            self.model_config.nodes.get_all()
        ):
            node_config = self.model_config.nodes.node(node_props)
            # if node_dict.is_visible is False:
            #     continue

            node_position = node_config.position
            # position is not available
            if node_position is None:
                # use pywr position if available
                pywr_position = node_config.pywr_position
                if pywr_position is not None:
                    node_position = self.to_px(pywr_position)
                else:
                    node_position = [
                        self.schematic_width / 2,
                        self.schematic_height / 2,
                    ]
                    self.nodes_wo_position += 1
                # set the new position and update the node dictionary
                node_props = self.model_config.nodes.set_position(
                    node_index=node_index, position=node_position
                )

            # draw the node
            self.add_node(node_props=node_props)

        # draw the edges
        model_edges = Edges(self.model_config)
        for source_node_name, source_node_obj in self.schematic_items.items():
            target_nodes = self.model_config.edges.get_targets(source_node_name)
            if target_nodes is not None:
                for target_node_name in target_nodes:
                    self.scene.addItem(
                        Edge(
                            source=source_node_obj,
                            target=self.schematic_items[target_node_name],
                            edge_color_name=model_edges.get_edge_color(
                                source_node_name
                            ),
                            hide_arrow=self.editor_settings.are_edge_arrows_hidden,
                        )
                    )

        # warn if some nodes do not have a position
        self.trigger_missing_pos_warning()

        # move nodes outside canvas
        self.adjust_nodes_initial_pos()

        if self.init is True:
            self.init = False

    def reload(self) -> None:
        """
        Reloads the scene and schematic.
        :return: None
        """
        self.scene.clear()
        self.add_scene_decorations()
        self.schematic_items = {}
        self.draw()

    def add_node(self, node_props: dict) -> SchematicItem:
        """
        Adds and registers a new graphical node to the schematic.
        :param node_props: The dictionary with the node properties.
        :return: The graphical node instance.
        """
        node_obj = SchematicItem(node_props=node_props, view=self)
        self.scene.addItem(node_obj)
        self.schematic_items[node_obj.name] = node_obj

        return node_obj

    def delete_node(self, node_name: str) -> list[list[str | int]]:
        """
        Deletes the provided node and its edges from the schematic and model
        configuration.
        :param node_name: The node name.
        :return: The list of model edges that were deleted.
        """
        # find the node shape on the schematic
        node_item = self.schematic_items[node_name]
        deleted_edges: list[list[str]] = []

        # delete edges on the schematic when node is source node
        for c_node in node_item.connected_nodes["target_nodes"]:
            edge_item = c_node.delete_edge(
                node_name=node_item.name, edge_type="source"
            )
            if edge_item:
                deleted_edges.append(self.delete_edge(edge_item))

        # delete edges on the schematic when node is target node
        for c_node in node_item.connected_nodes["source_nodes"]:
            edge_item = c_node.delete_edge(
                node_name=node_item.name, edge_type="target"
            )
            if edge_item:
                deleted_edges.append(self.delete_edge(edge_item))

        # remove the graphic item in schematic and model config
        self.model_config.nodes.delete(node_name)
        del self.schematic_items[node_name]
        self.scene.removeItem(node_item)

        return deleted_edges

    def delete_edge(self, edge_item: Edge) -> list[str | int]:
        """
        Deletes the edge from the schematic and model configuration.
        :param edge_item: The schematic Edge instance.
        :return: The deleted model edge (nodes and slot names).
        """
        self.scene.removeItem(edge_item)
        # delete edge from model config and returned deleted model edge
        edge, _ = self.model_config.edges.find_edge(
            edge_item.source.name, edge_item.target.name
        )
        self.model_config.edges.delete(edge)
        return edge

    def add_abort_node_connection_button(self) -> None:
        """
        Adds the abort node connection button.
        :return: None
        """
        button = QPushButton(
            "Select the node to connect. Press ESC or click here to abort"
        )
        button.setObjectName("abort-button")
        button.setStyleSheet(
            stylesheet_dict_to_str(
                {
                    "#abort-button": {
                        "background": Color("blue", 100).hex,
                        "border": 0,
                        "color": Color("blue", 600).hex,
                        ":hover": {
                            "background": Color("blue", 200).hex,
                            "border": 0,
                            "color": Color("blue", 800).hex,
                        },
                    }
                }
            )
        )
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.on_connect_node_end)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(button)
        button.hide()
        self.abort_node_connection_button = button

    def trigger_missing_pos_warning(self) -> None:
        """
        Warns if some nodes do not have a position.
        :return: None
        """
        if self.nodes_wo_position > 0:
            if self.nodes_wo_position == 1:
                text = (
                    f"{self.nodes_wo_position} node does not have a position "
                    + "assigned. This has been placed at\nthe schematic centre"
                    + "and may overlap with other nodes. Select and drag it\n"
                    + "to a new location to store its correct position."
                )
            else:
                text = (
                    f"{self.nodes_wo_position} nodes do not have a position "
                    + "assigned. These have been placed at\nthe schematic centre "
                    + "and may overlap with other nodes. Select and drag them\n"
                    + "to new locations to store their correct positions."
                )
            # noinspection PyUnresolvedReferences
            self.app.warning_info_message.emit(
                "Missing positions", text, "warn"
            )

    def adjust_nodes_initial_pos(self) -> None:
        """
         Moves nodes that are outside schematic onto the canvas.
        :return: None
        """
        moved_nodes_count = False
        for node in self.items():
            # ignore children and work on node groups only
            if not isinstance(node, SchematicItem):
                continue
            was_node_moved = node.adjust_node_position()

            if was_node_moved:
                node.save_position_if_moved()
                moved_nodes_count += 1

        # print message only when the schematic is first drawn
        if moved_nodes_count > 0 and self.init:
            if moved_nodes_count == 1:
                message = f"{moved_nodes_count} node was outside the schematic canvas "
                message += "and it has been\nmoved to lie within the canvas."
            else:
                message = (
                    f"{moved_nodes_count} nodes were outside the schematic "
                )
                message += (
                    "canvas and they have been\nmoved to lie within the canvas."
                )
            # noinspection PyUnresolvedReferences
            self.app.warning_info_message.emit(
                "Wrong node position", message, "info"
            )

        # disable decrease size buttons if at least one node is already on the edge
        # or has been moved
        self.toggle_schematic_size_buttons()

    def to_px(self, point: Sequence[float]) -> list[float]:
        """
        Transforms the point from the pywr coordinates to the schematic coordinates
        (i.e. pixels).
        :param point: The point to transform.
        :return: The transformed coordinates.
        """
        point_px = []
        px_sizes = [self.schematic_width, self.schematic_height]
        pywr_bound_size = self.pywr_bounds[1] - self.pywr_bounds[0]

        sign = [1, -1]
        for i, point_coordinate in enumerate(point):
            x_ratio = pywr_bound_size / px_sizes[i]
            point_px.append(
                round(
                    -(self.pywr_bounds[0] - sign[i] * point_coordinate)
                    / x_ratio,
                    4,
                )
            )
        return point_px

    def increase_height(self) -> None:
        """
        Increases the schematic height.
        :return: None
        """
        self.schematic_height = self.schematic_height + self.max_view_size_delta
        self.update_size()

        # re-enable button if it was disabled
        if self.app.actions.get("decrease-height").isEnabled() is False:
            self.enable_decrease_height_button(True)

    def decrease_height(self) -> None:
        """
        Decreases the schematic height.
        :return: None
        """
        max_min_bbox = SchematicBBoxUtils(
            self.items()
        ).min_max_bounding_box_coordinates
        node_max_y = max_min_bbox.max_y.value

        # height always changes from bottom - make sure that all the nodes fit in
        # the schematic
        view_size_delta = self.max_view_size_delta
        if self.schematic_height - node_max_y < view_size_delta:
            view_size_delta = self.schematic_height - node_max_y
            # lock decrease height button
            self.enable_decrease_height_button(False)

        self.schematic_height = self.schematic_height - view_size_delta
        self.update_size()

    def increase_width(self) -> None:
        """
        Increases the schematic width.
        :return: None
        """
        self.schematic_width = self.schematic_width + self.max_view_size_delta
        self.update_size()

        # re-enable button if it was disabled
        if self.app.actions.get("decrease-width").isEnabled() is False:
            self.enable_decrease_width_button(True)

    def decrease_width(self) -> None:
        """
        Decreases the schematic width.
        :return: None
        """
        max_min_bbox = SchematicBBoxUtils(
            self.items()
        ).min_max_bounding_box_coordinates
        node_max_x = max_min_bbox.max_x.value

        # width always changes from the left - make sure that all the nodes fit in the
        # schematic
        view_size_delta = self.max_view_size_delta
        if self.schematic_width - node_max_x < view_size_delta:
            view_size_delta = self.schematic_width - node_max_x
            # lock decrease width button
            self.enable_decrease_width_button(False)

        self.schematic_width = self.schematic_width - view_size_delta
        self.update_size()

    def update_scene_size(self) -> None:
        """
        Updates the scene size.
        :return: None
        """
        self.setSceneRect(
            -self.padding,
            -self.padding,
            self.schematic_width + self.padding * 2,
            self.schematic_height + self.padding * 2,
        )

    def update_size(self) -> None:
        """
        Updates the schematic size.
        :return: None
        """
        self.update_scene_size()
        self.canvas.update_size(self.schematic_width, self.schematic_height)
        self.model_config.update_schematic_size(
            [self.schematic_width, self.schematic_height]
        )

    def minimise_size(self) -> None:
        """
        Minimises the schematic.
        :return: None
        """
        max_min_bbox = SchematicBBoxUtils(
            self.items()
        ).min_max_bounding_box_coordinates
        self.schematic_width = max_min_bbox.max_x.value
        self.schematic_height = max_min_bbox.max_y.value

        self.update_size()
        self.enable_decrease_width_button(False)
        self.enable_decrease_height_button(False)

    def toggle_lock(self) -> None:
        """
        Locks the schematic so that any node cannot be moved.
        :return: None
        """
        for item in self.items():
            if isinstance(item, SchematicItem):
                item.setFlag(
                    QGraphicsItem.ItemIsMovable,
                    # this is False when schematic is going to be locked
                    self.editor_settings.is_schematic_locked,
                )

        self.editor_settings.save_schematic_lock(
            not self.editor_settings.is_schematic_locked
        )

    def toggle_schematic_size_buttons(self) -> None:
        """
        Toggles the status of the 'reduce schematic size' buttons. If one or more node
        is on the schematic edge, the buttons to reduce the schematic size must be
        disabled.
        :return: None
        """
        is_on_right_edge, is_on_bottom_edge = SchematicBBoxUtils(
            self.items()
        ).are_nodes_on_edges(self.schematic_width, self.schematic_height)
        self.enable_decrease_width_button(not is_on_right_edge)
        self.enable_decrease_height_button(not is_on_bottom_edge)

    def wheelEvent(self, event: PySide6.QtGui.QWheelEvent) -> None:
        """
        Handles zoom using the mouse wheel.
        :param event: The event being triggered.
        :return: None
        """
        self.scale_view(units_to_factor(event.angleDelta().y()))
        event.accept()

    def reset_scale(self) -> None:
        """
        Resets the scale to 100%.
        :return: None
        """
        self.setTransform(QtGui.QTransform())

    def scale_view(self, f: float) -> None:
        """
        Scales the view and handles the zoom buttons status.
        :param f: The scaling factor.
        :return: None
        """
        self.scaling_factor = round(
            self.transform().scale(f, f).mapRect(QRectF(0, 0, 1, 1)).width(), 4
        )

        if self.scaling_factor is not None:
            # zoom out button
            if self.scaling_factor <= self.min_zoom:
                self.app.actions.get("zoom-out").setDisabled(True)
            else:
                self.app.actions.get("zoom-out").setDisabled(False)
            # block scaling
            if self.scaling_factor < self.min_zoom:
                return

            if self.scaling_factor >= self.max_zoom:
                # zoom in button
                self.app.actions.get("zoom-in").setDisabled(True)
            else:
                self.app.actions.get("zoom-in").setDisabled(False)
            # block scaling
            if self.scaling_factor > self.max_zoom:
                return

            # zoom 100% button
            if self.scaling_factor == 1:
                self.app.actions.get("zoom-100").setDisabled(True)
            else:
                self.app.actions.get("zoom-100").setDisabled(False)

        self.app.editor_settings.save_zoom_level(self.scaling_factor)
        self.scale(f, f)

    @Slot(QPointF)
    def on_schematic_move(self, position: QPointF) -> None:
        """
        Slot called when the schematic is moved (by dragging it or when the toolbar
        button is clicked).
        :param position: The new position.
        :return: None
        """
        self.app.editor_settings.save_schematic_center(position)

    def center_view_on(self, position: QPointF | None = None) -> None:
        """
        Centers the view on the provided position. If this is None, the schematic is
        centered on the scene center.
        :param position: The position to center the schematic on. Optional.
        :return: None
        """
        if not position:  # can be also False when triggered from QAction
            position = self.scene.sceneRect().center()
        self.centerOn(position)
        # noinspection PyUnresolvedReferences
        self.schematic_move_event.emit(position)

    def fit_view(self) -> None:
        """
        Centers the view to the scene center.
        :return: None
        """
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def select_node_by_name(self, node_name: str) -> None:
        """
        Marks a node as selected by identifying the node with its name.
        :param node_name: The node name
        :return: None
        """
        for node in self.items():
            if isinstance(node, SchematicItem) and node.name == node_name:
                node.setSelected(True)
                break

    def toggle_labels(self) -> None:
        """
        Shows or hides the node labels on the schematic.
        :return: None
        """
        for node in self.items():
            if isinstance(node, SchematicItem):
                node.label.toggle_label()

        self.editor_settings.save_hide_labels(
            not self.editor_settings.are_labels_hidden
        )

    def toggle_arrows(self) -> None:
        """
        Shows or hides the edge arrows on the schematic.
        :return: None
        """
        for item in self.items():
            if isinstance(item, Edge):
                item.toggle_arrow()

        self.editor_settings.save_hide_arrows(
            not self.editor_settings.are_edge_arrows_hidden
        )

    def export_current_view(self) -> None:
        # # image = QImage(self.scene.sceneRect().size().toSize(), QImage.Format_RGBA64)
        # image = QPixmap(self.scene.sceneRect().size().toSize())
        # # image.fill(Qt.GlobalColor.transparent)
        # p = QPainter(image)
        #
        # self.scene.render(p, self.scene.itemsBoundingRect())
        # p.end()
        # image.save('test.png')
        # return
        file = QFileDialog().getSaveFileName(
            self, "Save current view as image", "", "PNG (*.png)"
        )
        file_name = file[0]
        # TODO: to clipboard?

        if len(file_name) > 0:
            self.scene.clearSelection()
            pixmap = self.grab()
            pixmap.save(file_name)
            self.app.statusBar().showMessage(
                f"Exported current view as {file_name}"
            )
        else:
            self.app.statusBar().showMessage("Schematic export aborted")

    def enable_decrease_width_button(self, enable: bool = False) -> None:
        """
        Enables or disables the button to decrease the schematic width.
        :param enable: Whether to enable the button. If False the button is disabled.
        :return: None
        """
        self.app.actions.get("decrease-width").setEnabled(enable)

    def enable_decrease_height_button(self, enable: bool = False) -> None:
        """
        Enables or disables the button to decrease the schematic height.
        :param enable: Whether to enable the button. If False the button is disabled.
        :return: None
        """
        self.app.actions.get("decrease-height").setEnabled(enable)

    def select_all_items(self) -> None:
        """
        Select all items on the schematic.
        :return: None
        """
        for item in self.items():
            item.setSelected(True)

    def de_select_all_items(self) -> None:
        """
        De-select all items on the schematic.
        :return: None
        """
        self.scene.clearSelection()

    @Slot()
    def on_delete_nodes(self, nodes: list["SchematicItem"]) -> None:
        """
        Deletes the nodes and their edges from the schematic and model configuration.
        :return: None
        """
        command = DeleteNodeCommand(schematic=self, selected_nodes=nodes)
        self.app.undo_stack.push(command)

    @Slot(SchematicItem)
    def on_connect_node_start(self, node: "SchematicItem") -> None:
        """
        Connects the node to another one on the schematic.
        :param node: The node where the new edge needs to start.
        :return: None
        """
        self.connecting_node_props.enabled = True
        self.connecting_node_props.source_node = node
        self.viewport().setCursor(Qt.CrossCursor)
        self.abort_node_connection_button.show()
        self.app.actions.get("add-edge").setEnabled(False)

        # disable actions
        for action_key in [
            "remove-edges",
            "edit-node",
            "delete-node",
            "select-all",
            "select-none",
        ]:
            self.app.actions.get(action_key).setEnabled(False)

        # enable connecting mode for nodes. Exclude virtual and already connected nodes
        for item in self.items():
            item: SchematicItem
            if isinstance(item, SchematicItem) and item != node:
                if item.is_connectable(node):
                    item.connecting_mode_on = True
                    item.setFlag(QGraphicsItem.ItemIsMovable, False)
                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                    item.setOpacity(item.disabled_node_opacity)
                    item.setEnabled(False)

        # draw new temporary edge
        new_temp_edge = TempEdge(node, self)
        self.connecting_node_props.temp_edge = new_temp_edge
        self.scene.addItem(new_temp_edge)

    @Slot(SchematicItem)
    def on_connect_node_end(
        self, target_node: Union["SchematicItem", None] = None
    ) -> None:
        """
        Actions to perform after a node has been connected.
        :param target_node: The target node to connect the new edge to. This is
        supplied when the user click on a node on the schematic (via mousePressEvent).
        If the user aborts the connection or clicks on the canvas, the target is None.
        :return: None
        """
        source_node = self.connecting_node_props.source_node
        if source_node is None:
            return

        # remove the temporary dge
        self.scene.removeItem(self.connecting_node_props.temp_edge)

        # create the new edge if the target mode is available (this may be False or
        # None when the connection is aborted)
        if target_node:
            command = ConnectNodeCommand(
                schematic=self,
                source_node_name=source_node.name,
                target_node_name=target_node.name,
            )
            self.app.undo_stack.push(command)

        # reset
        self.connecting_node_props.reset()
        self.abort_node_connection_button.hide()
        self.viewport().setCursor(Qt.ArrowCursor)
        for item in self.items():
            if isinstance(item, SchematicItem):
                # restore style and behaviour
                item.setFlag(
                    QGraphicsItem.ItemIsMovable,
                    not self.editor_settings.is_schematic_locked,
                )
                item.setEnabled(True)
                item.connecting_mode_on = False
                if item.opacity() == item.disabled_node_opacity:
                    item.setOpacity(1)

        self.de_select_all_items()
        for action_key in ["select-all", "select-none"]:
            self.app.actions.get(action_key).setEnabled(True)

    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        """
        Enables the schematic panning on mouse click only when the canvas is selected.
        :param event: The event being triggered.
        :return: None
        """
        if event.button() == Qt.LeftButton:
            # enable selection rectangle
            if event.modifiers() == Qt.ControlModifier:
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            else:
                items = self.items(event.pos())
                item_types = map(type, items)
                # enable canvas dragging
                if len(items) > 0 and SchematicItem not in item_types:
                    self.de_select_all_items()
                    self.canvas_drag = True
                    self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        """
        Handles drag, node position saving and toolbar buttons.
        :param event: The event being triggered.
        :return: None
        """
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            # perform action on selected nodes
            if self.canvas_drag is False:
                # save position only if the nodes were moved
                if any(
                    [
                        n.has_position_changed()
                        for n in self.scene.selectedItems()
                    ]
                ):
                    command = MoveNodeCommand(
                        schematic=self,
                        selected_nodes=self.scene.selectedItems(),
                    )
                    self.app.undo_stack.push(command)
            else:
                # export the new scene center
                items = self.items(event.pos())
                item_types = map(type, items)
                if len(items) > 0 and SchematicItem not in item_types:
                    center = (
                        self.mapToScene(self.viewport().geometry())
                        .boundingRect()
                        .center()
                    )
                    # noinspection PyUnresolvedReferences
                    self.schematic_move_event.emit(center)

            # toggle the status of the 'reduce schematic size' buttons after a node
            # is moved
            self.toggle_schematic_size_buttons()

            # disable drag of canvas regardless of item
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.canvas_drag = False

            # connect nodes when mode is enabled
            items = self.items(event.pos())
            if self.connecting_node_props.enabled is True:
                # force cursor again after dragging
                self.viewport().setCursor(Qt.CrossCursor)

                valid_items = [
                    item for item in items if isinstance(item, SchematicItem)
                ]
                if len(valid_items) > 0:
                    selected_item = valid_items[0]
                    if self.connecting_node_props.source_node.is_connectable(
                        selected_item
                    ):
                        # noinspection PyUnresolvedReferences
                        self.connect_node_event.emit(valid_items[0])
                    else:
                        # noinspection PyUnresolvedReferences
                        self.app.warning_info_message.emit(
                            "Connect node",
                            "You cannot connect "
                            + f"{self.connecting_node_props.source_node.name} to "
                            + f"{selected_item.name} because the node is virtual or is "
                            + "already connected",
                            "warn",
                        )

    def mouseMoveEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        """
        Handles actions when the mouse pointer moves.
        :param event: The event being triggered.
        :return: None
        """
        if self.connecting_node_props.enabled:
            # Updated the temporary edge position
            self.connecting_node_props.temp_edge.adjust(
                self.mapToScene(event.pos())
            )

        super().mouseMoveEvent(event)

    def dragMoveEvent(self, event: PySide6.QtGui.QDragMoveEvent) -> None:
        """
        Accepts the drag move events.
        :param event: The event being triggered.
        :return: None
        """
        event.accept()

    def dragEnterEvent(self, event: PySide6.QtGui.QDragEnterEvent) -> None:
        """
        Accepts the drag enter events.
        :param event: The event being triggered.
        :return: None
        """
        super().dragEnterEvent(event)
        # noinspection PyTypeChecker
        panel: NodesLibraryPanel = self.app.findChild(NodesLibraryPanel)

        if (
            event.mimeData().hasText()
            and isinstance(event.mimeData().text(), str)
            and event.mimeData().text() in panel.node_dict
        ):
            event.accept()
            self.update()
        else:
            event.setAccepted(False)

    def dropEvent(self, event: PySide6.QtGui.QDropEvent) -> None:
        """
        Adds the dropped node to the schematic.
        :param event: The event being triggered.
        :return: None
        """
        super().dropEvent(event)
        if event.mimeData().hasText():
            node_type = event.mimeData().text()
            # add the new node to the model
            node_props = NodeConfig.create(
                name=f"Node {QUuid().createUuid().toString()[1:7]}",
                node_type=node_type,
                position=self.mapToScene(event.pos()).toTuple(),
            )

            # register the action in the undo stack
            command = AddNodeCommand(schematic=self, added_node_dict=node_props)
            self.app.undo_stack.push(command)
        self.update()

    def on_scene_change(self) -> None:
        """
        Checks when new items are added to the schematic.
        :return: None
        """
        # when there is only one item (the canvas), prevent the schematic from being
        # minimised
        if len(self.scene.items()) == 1:
            enabled = False
        else:
            enabled = True
        if self.app.actions.get("minimise").isEnabled() != enabled:
            self.app.actions.get("minimise").setEnabled(enabled)

    @Slot()
    def on_selection_changed(self) -> None:
        """
        Slot called when the selection on the scene changes. This is used to
        enable/disable the toolbar buttons.
        :return: None
        """
        if self.connecting_node_props.enabled is True:
            return

        panel = self.app.toolbar.tabs["Nodes"].panels["Operations"]
        delete_edge_button = panel.buttons["Disconnect"]
        delete_edge_action = self.app.actions.get("remove-edges")
        add_edge_action = self.app.actions.get("add-edge")
        edit_node_action = self.app.actions.get("edit-node")
        delete_node_action = self.app.actions.get("delete-node")
        select_node_action = self.app.actions.get("select-none")

        # always disconnect the signals
        try:
            # noinspection PyUnresolvedReferences
            edit_node_action.triggered.disconnect()
        except RuntimeError:
            pass
        try:
            # noinspection PyUnresolvedReferences
            delete_node_action.triggered.disconnect()
        except RuntimeError:
            pass

        selected_items: list["SchematicItem"] = self.scene.selectedItems()
        items_count = len(selected_items)
        if items_count == 1:
            item = selected_items[0]
            # add and delete edge
            if not selected_items[0].model_node.is_virtual:
                # if there are no connected nodes, keep the button disabled
                if item.add_delete_edge_actions(
                    delete_edge_button.dropdown_menu
                ):
                    delete_edge_action.setDisabled(False)
                else:
                    delete_edge_action.setDisabled(True)

                add_edge_action.triggered.connect(
                    lambda *args, node=item: self.on_connect_node_start(node)
                )
                add_edge_action.setDisabled(False)

            # edit node
            edit_node_action.triggered.connect(item.on_edit_node)
            edit_node_action.setDisabled(False)

            # delete node
            delete_node_action.triggered.connect(item.on_delete_node)
            delete_node_action.setDisabled(False)

            # select none
            select_node_action.setDisabled(False)
        elif items_count > 1:
            # delete multiple selected nodes
            # noinspection PyDefaultArgument
            delete_node_action.triggered.connect(
                lambda *args, nodes=selected_items: self.on_delete_nodes(nodes)
            )

        # restore state
        if items_count == 0:
            edit_node_action.setDisabled(True)
            delete_node_action.setDisabled(True)
            select_node_action.setDisabled(True)

        if items_count != 1:
            add_edge_action.setDisabled(True)
            delete_edge_action.setDisabled(True)
            edit_node_action.setDisabled(True)
