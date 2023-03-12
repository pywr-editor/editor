import inspect
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

from pywr_editor.dialogs import InspectorTree
from pywr_editor.model import (
    BaseShape,
    Edges,
    LineArrowShape,
    ModelConfig,
    NodeConfig,
    RectangleShape,
    TextShape,
)
from pywr_editor.node_shapes import get_node_icon_classes
from pywr_editor.schematic import (
    AbstractSchematicItem,
    AbstractSchematicShape,
    AddNodeCommand,
    AddShapeCommand,
    ConnectNodeCommand,
    DeleteItemCommand,
    MoveItemCommand,
    SchematicArrow,
    SchematicBBoxUtils,
    SchematicNode,
    SchematicRectangle,
    SchematicText,
    scaling_factor,
    units_to_factor,
)
from pywr_editor.style import Color, stylesheet_dict_to_str
from pywr_editor.toolbar import LibraryPanel

from .canvas import SchematicCanvas
from .connecting_node_props import ConnectingNodeProps
from .edge import Edge, TempEdge

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
    connect_node_event = Signal(SchematicNode)
    """ event emitted when a node is being connected to another """
    min_zoom = scaling_factor("zoom-out", 3)
    """ min zoom factor"""
    max_zoom = scaling_factor("zoom-in", 3)
    """ max zoom factor"""
    shape_class_map = {
        "TextShape": SchematicText,
        "RectangleShape": SchematicRectangle,
        "LineArrowShape": SchematicArrow,
    }
    """ map of model class to schematic class for shapes """

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
        self.node_items: dict[str, SchematicNode] = {}
        self.shape_items: dict[
            str, SchematicText | SchematicRectangle | SchematicArrow
        ] = {}

        self.schematic_move_event.connect(self.on_schematic_move)
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
        Draw the schematic.
        :return: None
        """
        # draw the nodes
        for node_index, node_props in enumerate(
            self.model_config.nodes.get_all()
        ):
            node_config = self.model_config.nodes.node(node_props)
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
        for source_node_name, source_node_obj in self.node_items.items():
            target_nodes = self.model_config.edges.get_targets(source_node_name)
            if target_nodes is not None:
                for target_node_name in target_nodes:
                    self.scene.addItem(
                        Edge(
                            source=source_node_obj,
                            target=self.node_items[target_node_name],
                            edge_color_name=model_edges.get_edge_color(
                                source_node_name
                            ),
                            hide_arrow=self.editor_settings.are_edge_arrows_hidden,
                        )
                    )

        # warn if some nodes do not have a position
        self.trigger_missing_pos_warning()

        # draw the shapes
        for shape_obj in self.model_config.shapes.get_all():
            self.add_shape(shape_obj)

        # move items that are outside the canvas edges
        self.adjust_items_initial_pos()

        if self.init is True:
            self.init = False

    def reload(self) -> None:
        """
        Reloads the scene and schematic.
        :return: None
        """
        self.scene.clear()
        self.add_scene_decorations()
        self.node_items = {}
        self.draw()

    def add_node(self, node_props: dict) -> SchematicNode:
        """
        Add a new graphical node to the schematic.
        :param node_props: The dictionary with the node properties.
        :return: The graphical node instance.
        """
        node_obj = SchematicNode(node_props=node_props, view=self)
        self.scene.addItem(node_obj)
        self.node_items[node_obj.name] = node_obj

        return node_obj

    def delete_node(self, node_name: str) -> list[list[str | int]]:
        """
        Deletes the provided node and its edges from the schematic and model
        configuration.
        :param node_name: The node name.
        :return: The list of model edges that were deleted.
        """
        # find the node shape on the schematic
        node_item = self.node_items[node_name]
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
        del self.node_items[node_name]
        self.scene.removeItem(node_item)

        return deleted_edges

    def add_shape(self, shape_obj: BaseShape) -> None:
        """
        Add a shape to the schematic.
        :param shape_obj: The instance of the shape object.
        :return: None
        """
        shape = self.shape_class_map[shape_obj.__class__.__name__](
            shape_id=shape_obj.id, shape=shape_obj, view=self
        )
        self.shape_items[shape_obj.id] = shape
        self.scene.addItem(shape)

    def delete_shape(self, shape_id: str) -> None:
        """
        Delete the shape matching the provided ID.
        :param shape_id: The shape ID.
        :return: None.
        """
        if shape_id not in self.shape_items:
            return

        shape_item = self.shape_items[shape_id]
        # remove the graphic item in schematic and model config
        self.model_config.shapes.delete(shape_item.id)
        del self.shape_items[shape_id]
        self.scene.removeItem(shape_item)

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

    def adjust_items_initial_pos(self) -> None:
        """
        Move items that are outside the schematic onto the canvas.
        :return: None
        """
        moved_items_count = False
        for item in self.items():
            # ignore children and work on node groups and shapes only
            if not isinstance(item, (SchematicNode, AbstractSchematicShape)):
                continue

            was_item_moved = item.adjust_position()
            if was_item_moved:
                item.save_position_if_moved()
                moved_items_count += 1

        # print message only when the schematic is first drawn
        if moved_items_count > 0 and self.init:
            if moved_items_count == 1:
                message = (
                    f"{moved_items_count} item was outside the schematic canvas "
                    + "and this was\nmoved to lie within the canvas limits."
                )
            else:
                message = (
                    f"{moved_items_count} items were outside the schematic "
                    + "canvas and these were\nmoved to lie within the canvas limits."
                )
            self.app.warning_info_message.emit(
                "Wrong item position", message, "info"
            )

        # disable decrease size buttons if at least one item is already on the edge
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

    @Slot()
    def increase_height(self) -> None:
        """
        Increases the schematic height.
        :return: None
        """
        self.schematic_height = self.schematic_height + self.max_view_size_delta
        self.update_size()

        # re-enable button if it was disabled
        if self.app.app_actions.get("decrease-height").isEnabled() is False:
            self.enable_decrease_height_button(True)

    @Slot()
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

    @Slot()
    def increase_width(self) -> None:
        """
        Increases the schematic width.
        :return: None
        """
        self.schematic_width = self.schematic_width + self.max_view_size_delta
        self.update_size()

        # re-enable button if it was disabled
        if self.app.app_actions.get("decrease-width").isEnabled() is False:
            self.enable_decrease_width_button(True)

    @Slot()
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
            if isinstance(item, (SchematicNode, AbstractSchematicShape)):
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
        ).are_items_on_edges(self.schematic_width, self.schematic_height)
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
                self.app.app_actions.get("zoom-out").setDisabled(True)
            else:
                self.app.app_actions.get("zoom-out").setDisabled(False)
            # block scaling
            if self.scaling_factor < self.min_zoom:
                return

            if self.scaling_factor >= self.max_zoom:
                # zoom in button
                self.app.app_actions.get("zoom-in").setDisabled(True)
            else:
                self.app.app_actions.get("zoom-in").setDisabled(False)
            # block scaling
            if self.scaling_factor > self.max_zoom:
                return

            # zoom 100% button
            if self.scaling_factor == 1:
                self.app.app_actions.get("zoom-100").setDisabled(True)
            else:
                self.app.app_actions.get("zoom-100").setDisabled(False)

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

    @Slot()
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

    @Slot()
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
            if isinstance(node, SchematicNode) and node.name == node_name:
                node.setSelected(True)
                break

    @Slot()
    def toggle_labels(self) -> None:
        """
        Shows or hides the node labels on the schematic.
        :return: None
        """
        for node in self.items():
            if isinstance(node, SchematicNode):
                node.label.toggle_label()

        self.editor_settings.save_hide_labels(
            not self.editor_settings.are_labels_hidden
        )

    @Slot()
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

    @Slot()
    def export_current_view(self) -> None:
        """
        Exports the current view.
        :return: None
        """
        file = QFileDialog().getSaveFileName(
            self, "Save current view as image", "", "PNG (*.png)"
        )
        file_name = file[0]

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
        self.app.app_actions.get("decrease-width").setEnabled(enable)

    def enable_decrease_height_button(self, enable: bool = False) -> None:
        """
        Enables or disables the button to decrease the schematic height.
        :param enable: Whether to enable the button. If False the button is disabled.
        :return: None
        """
        self.app.app_actions.get("decrease-height").setEnabled(enable)

    def set_run_mode(self, enable: bool) -> None:
        """
        Enables the run mode when the model is running.
        :param enable: Whether the model is running.
        :return: None
        """
        if enable:
            self.canvas.setOpacity(0.7)
        else:
            self.canvas.setOpacity(1)

        for item in self.items():
            if isinstance(item, SchematicNode):
                if enable:
                    # lock node position and selection
                    item.setFlag(QGraphicsItem.ItemIsMovable, False)
                    item.setFlag(QGraphicsItem.ItemIsSelectable, False)

                    # draw new tooltip
                    model = self.app.run_widget.worker.pywr_model

                    cell_style = "style='padding:2px 6px;"
                    cell_style += (
                        f"border:1px solid {Color('neutral', 400).hex}'"
                    )

                    tooltip_text = "<table>"
                    tooltip_text += (
                        "<tr><td colspan='2'><b style='font-size:12pt'>"
                    )
                    tooltip_text += f"{item.name}</td></tr>"

                    node = model.nodes[item.name]
                    all_attributes = inspect.getmembers(
                        node,
                        lambda a: not inspect.isroutine(a),
                    )
                    for (
                        attr_raw_name,
                        result_data,
                    ) in InspectorTree.get_node_value_dict(
                        model, all_attributes
                    ).items():
                        if attr_raw_name == "prev_flow":
                            continue
                        attr_name = item.model_node.humanise_attribute_name(
                            attr_raw_name
                        )
                        tooltip_text += "<tr>"
                        # data with scenarios
                        if result_data["has_scenarios"]:
                            tooltip_text += f"<td colspan='2'>{attr_name} "
                            tooltip_text += "<table style='margin-left:10px;"
                            tooltip_text += "border-collapse:collapse'>"
                            tooltip_text += (
                                f"<tr><td {cell_style}><b>Combination</b>"
                            )
                            tooltip_text += (
                                f"</td><td {cell_style}><b>Value</b></td></tr>"
                            )
                            for sc_value in result_data["data"]:
                                tooltip_text += f"<tr><td {cell_style}>"
                                tooltip_text += f"{sc_value['name']}</td>"
                                tooltip_text += (
                                    f"<td {cell_style}>{sc_value['value']}"
                                )
                                tooltip_text += "</td></tr>"
                            tooltip_text += "</table></td>"
                        # single value
                        else:
                            tooltip_text += f"<td>{attr_name}:</td>"
                            tooltip_text += (
                                f"<td>{result_data['data']['value']}</td>"
                            )
                        tooltip_text += "</tr>"
                    tooltip_text += "</table>"
                else:
                    # unlock node position and selection
                    item.setFlag(QGraphicsItem.ItemIsMovable, True)
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)

                    # restore tooltip
                    tooltip_text = item.tooltip_text

                item.setToolTip(tooltip_text)

    @Slot()
    def select_all_items(self) -> None:
        """
        Select all items on the schematic.
        :return: None
        """
        for item in self.items():
            item.setSelected(True)

    @Slot()
    def de_select_all_items(self) -> None:
        """
        De-select all items on the schematic.
        :return: None
        """
        self.scene.clearSelection()

    @Slot(list)
    def on_delete_item(self, items: list["AbstractSchematicItem"]) -> None:
        """
        Delete the provided list of nodes (and their edges), and annotation shapes from
        the schematic and model configuration.
        :return: None
        """
        command = DeleteItemCommand(schematic=self, selected_items=items)
        self.app.undo_stack.push(command)

    @Slot(SchematicNode)
    def on_connect_node_start(self, node: "SchematicNode") -> None:
        """
        Connects the node to another one on the schematic.
        :param node: The node where the new edge needs to start.
        :return: None
        """
        self.connecting_node_props.enabled = True
        self.connecting_node_props.source_node = node
        self.viewport().setCursor(Qt.CrossCursor)
        self.abort_node_connection_button.show()
        self.app.app_actions.get("add-edge").setEnabled(False)

        # disable actions
        for action_key in [
            "remove-edges",
            "edit-node",
            "delete-node",
            "select-all",
            "select-none",
        ]:
            self.app.app_actions.get(action_key).setEnabled(False)

        # enable connecting mode for nodes. Exclude virtual and already connected nodes
        for item in self.items():
            item: SchematicNode
            if isinstance(item, SchematicNode) and item != node:
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

    @Slot(SchematicNode)
    def on_connect_node_end(
        self, target_node: Union["SchematicNode", None] = None
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
            if isinstance(item, SchematicNode):
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
            self.app.app_actions.get(action_key).setEnabled(True)

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
                # check that no selectable item was selected and canvas can be dragged
                is_selectable = map(
                    lambda item: isinstance(
                        item, (SchematicNode, AbstractSchematicShape)
                    ),
                    items,
                )
                # enable canvas dragging
                if len(items) > 0 and not any(is_selectable):
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
                items: list[
                    "AbstractSchematicItem"
                ] = self.scene.selectedItems()
                # save position only if the nodes were moved
                if any([n.has_position_changed() for n in items]):
                    command = MoveItemCommand(
                        schematic=self, selected_items=items
                    )
                    self.app.undo_stack.push(command)
            else:
                # export the new scene center
                items = self.items(event.pos())
                # check that no selectable item was selected
                is_selectable = map(
                    lambda item: isinstance(item, SchematicNode)
                    or isinstance(item, AbstractSchematicShape),
                    items,
                )
                if len(items) > 0 and not any(is_selectable):
                    center = (
                        self.mapToScene(self.viewport().geometry())
                        .boundingRect()
                        .center()
                    )
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
                    item for item in items if isinstance(item, SchematicNode)
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
        panel: LibraryPanel = self.app.findChild(LibraryPanel)

        if (
            event.mimeData().hasText()
            and isinstance(event.mimeData().text(), str)
            # item is a node or a shape
            and (
                event.mimeData().text() in panel.node_dict
                or "Shape." in event.mimeData().text()
            )
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
            mime_type = event.mimeData().text()
            position = self.mapToScene(event.pos()).toTuple()
            position = tuple(map(lambda x: round(x, 5), position))
            shape_obj = None

            if "Shape." in mime_type:
                if "TextShape" in mime_type:
                    shape_obj = TextShape.create(position=position)

                elif "RectangleShape" in mime_type:
                    shape_obj = RectangleShape.create(
                        position=position,
                        size=[
                            SchematicRectangle.min_rect_width,
                            SchematicRectangle.min_rect_height,
                        ],
                    )
                elif "ArrowShape" in mime_type:
                    shape_obj = LineArrowShape.create(
                        position=position,
                        length=SchematicArrow.min_line_length,
                        angle=-45,
                    )

                # push command
                if shape_obj:
                    command = AddShapeCommand(
                        schematic=self, added_shape_obj=shape_obj
                    )
                    self.app.undo_stack.push(command)
            else:
                # add the new node to the model
                node_props = NodeConfig.create(
                    name=f"Node {QUuid().createUuid().toString()[1:7]}",
                    node_type=mime_type.lower(),
                    position=position,
                )

                # register the action in the undo stack
                command = AddNodeCommand(
                    schematic=self, added_node_dict=node_props
                )
                self.app.undo_stack.push(command)
        self.update()

    @Slot()
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
        if self.app.app_actions.get("minimise").isEnabled() != enabled:
            self.app.app_actions.get("minimise").setEnabled(enabled)

    @property
    def selected_nodes(self) -> list["SchematicNode"]:
        """
        Returns a list of selected nodes.
        :return: The list of selected SchematicItem instances.
        """
        return [
            item
            for item in self.scene.selectedItems()
            if isinstance(item, SchematicNode)
        ]

    @Slot()
    def on_selection_changed(self) -> None:
        """
        Slot called when the selection on the scene changes. This is used to
        enable/disable the toolbar buttons for nodes only. Annotation shapes
        are ignored.
        :return: None
        """
        if self.connecting_node_props.enabled is True:
            return

        panel = self.app.toolbar.tabs["Schematic"].panels["Operations"]
        delete_edge_button = panel.buttons["Disconnect"]
        delete_edge_action = self.app.app_actions.get("remove-edges")
        add_edge_action = self.app.app_actions.get("add-edge")
        edit_node_action = self.app.app_actions.get("edit-node")
        delete_node_action = self.app.app_actions.get("delete-node")
        select_node_action = self.app.app_actions.get("select-none")

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

        selected_items = self.selected_nodes

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
            delete_node_action.triggered.connect(item.on_delete_item)
            delete_node_action.setDisabled(False)

            # select none
            select_node_action.setDisabled(False)
        elif items_count > 1:
            # delete multiple selected nodes
            # noinspection PyDefaultArgument
            delete_node_action.triggered.connect(
                lambda *args, nodes=selected_items: self.on_delete_item(nodes)
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
