from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import QPoint, Qt, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QStyle,
    QStyledItemDelegate,
    QTreeWidget,
    QTreeWidgetItem,
)

from pywr_editor.dialogs import (
    ParametersDialog,
    ParametersWidget,
    RecordersDialog,
    RecordersWidget,
    TablesDialog,
    TablesWidget,
)
from pywr_editor.model import Constants, ModelConfig
from pywr_editor.style import Color, stylesheet_dict_to_str
from pywr_editor.widgets import ContextualMenu

from .expanded_item_states import ExpandedItemStates
from .tree_widget_node import TreeWidgetNode
from .tree_widget_parameter import TreeWidgetParameter, TreeWidgetParameterName
from .tree_widget_recorder import TreeWidgetRecorder, TreeWidgetRecorderName
from .tree_widget_table import TreeWidgetTable

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class ComponentsTree(QTreeWidget):
    def __init__(self, model_config: ModelConfig, parent: "MainWindow"):
        """
        Initialises the component tree.
        :param model_config: The ModelConfig instance.
        :param parent: The parent window.
        """
        super().__init__(parent)
        self.parent = parent
        self.model_config = model_config
        self.json = model_config.json
        self.items: dict[str, QTreeWidgetItem] = {}
        self.expanded_state = ExpandedItemStates()
        self.init: bool = True
        # add the context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.customContextMenuRequested.connect(self.on_context_menu)
        # locate item on schematic on mouse click
        # noinspection PyUnresolvedReferences
        self.itemClicked.connect(self.on_item_click)
        # store the expanded state when an item is expanded via the arrows or by
        # double-clicking
        # noinspection PyUnresolvedReferences
        self.itemExpanded.connect(self.on_expanded_item)
        # noinspection PyUnresolvedReferences
        self.itemCollapsed.connect(self.on_collapse_item)

        # remove focus
        self.setFocusPolicy(Qt.NoFocus)
        # bold font on selected
        self.setItemDelegate(StyleDelegate(self))
        self.setHeaderLabels(("Component", "Value"))
        self.setColumnCount(2)

        self.header().resizeSection(0, 200)
        self.header().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.header().setStretchLastSection(False)
        self.setStyleSheet(self.stylesheet)

    def draw(self) -> None:
        """
        Draws the widget.
        :return: None
        """
        # enable sorting
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        self._populate_model_info()
        self._populate_timestepper()
        self._populate_nodes()
        self._populate_parameters()
        self._populate_tables()
        self._populate_recorders()
        self._populate_scenarios()
        self.insertTopLevelItems(0, [group for group in self.items.values()])

        # do not let user sort columns
        self.setSortingEnabled(False)
        self.init = False

    def reload(self) -> None:
        """
        Reloads the tree with the saved expanded state.
        :return: None
        """
        self.clear()
        self.draw()

        self.collapseAll()
        # expand items by name whose state was stored. These are node's and
        # parameter's names that are unique
        for name in self.expanded_state.get_all():
            targets = self.findItems(
                name, Qt.MatchExactly | Qt.MatchRecursive, 0
            )
            for target in targets:
                if self.expanded_state.is_state_stored(target):
                    target.setExpanded(True)

    def _populate_nodes(self) -> None:
        """
        Populates the tree widget with the nodes.
        :return: None
        """
        # initialise the node list
        nodes = {
            **{
                node_name: []
                for node_name in self.model_config.pywr_node_data.names
            },
            **{Constants.CUSTOM_NODE_GROUP_NAME.value: []},
        }

        # group nodes by type
        model_nodes = self.model_config.nodes
        for node_dict in model_nodes.get_all():
            group = model_nodes.node(node_dict).humanise_node_type
            item = TreeWidgetNode(
                node_dict=node_dict,
                model_config=self.model_config,
            )
            self.expanded_state.store_state(item)

            nodes[group].append(item)

        # add groups
        parent_item = QTreeWidgetItem(self)
        parent_item.setText(0, "Nodes")

        for node_group, nodes_list in nodes.items():
            nodes_count = len(nodes_list)
            if nodes_count == 0:
                continue
            node_group_item = QTreeWidgetItem(parent_item)
            node_group_item.setText(0, f"{node_group} ({nodes_count})")
            node_group_item.addChildren(nodes_list)
            parent_item.addChild(node_group_item)
            self.expanded_state.store_state(node_group_item)

        if self.init:
            self.expanded_state.add(parent_item, True)
        else:  # always store the state
            self.expanded_state.store_state(parent_item)

        self.items["nodes"] = parent_item

    def _populate_parameters(self) -> None:
        """
        Populates the tree widget with the parameters.
        :return: None
        """
        # parameters
        if self.model_config.parameters is None:
            return

        parent_item = QTreeWidgetItem(self)
        parent_item.setText(0, "Parameters")

        for name, config in self.model_config.parameters.get_all().items():
            sub_item = TreeWidgetParameterName(name=name)
            sub_item.setText(0, name)
            param_config_item = TreeWidgetParameter(
                parameter_config=config,
                model_config=self.model_config,
                parent=sub_item,
            )
            self.expanded_state.store_state(sub_item)
            sub_item.addChildren(param_config_item.items)
            parent_item.addChild(sub_item)

        if self.init:
            self.expanded_state.add(parent_item, True)
        else:
            self.expanded_state.store_state(parent_item)
        self.items["parameters"] = parent_item

    def _populate_timestepper(self) -> None:
        """
        Populates the tree widget for the timestepper key.
        :return: None
        """
        # timestepper
        if self.model_config.timestepper is None:
            return

        time_step_info = QTreeWidgetItem(self)
        time_step_info.setText(0, "Timestepper")
        for key, value in self.model_config.timestepper.items():
            item = QTreeWidgetItem(time_step_info)
            item.setText(0, key.title())
            item.setText(1, str(value))

        self.items["timestepper"] = time_step_info

    def _populate_model_info(self) -> None:
        """
        Populates the tree widget with the model information.
        :return: None
        """
        if self.model_config.metadata is None:
            return

        model_items = QTreeWidgetItem(self)
        model_items.setText(0, "Model")

        # metadata
        for key, value in self.model_config.metadata.items():
            if (
                isinstance(value, str) and len(value) == 0
            ):  # do not print empty fields
                continue

            item = QTreeWidgetItem(model_items)
            item.setText(0, self.humanise_key(key))
            if key == "description":
                item.setText(1, str(value)[0:100])
            else:
                item.setText(1, str(value))
            item.setToolTip(1, str(value))

        # file information
        fields = ["file_name", "size", "created_on"]
        for field in fields:
            value = getattr(self.model_config.file, field)
            if value is None:
                continue

            item = QTreeWidgetItem(model_items)
            item.setText(0, self.humanise_key(field))
            item.setText(1, str(value))
            item.setToolTip(1, str(value))

        if self.init:
            self.expanded_state.add(model_items, True)
        else:
            self.expanded_state.store_state(model_items)
        self.items["model"] = model_items

    def _populate_tables(self) -> None:
        """
        Populates the tree widget with the tables.
        :return: None
        """
        if self.model_config.tables.get_all() is None:
            return

        tables = QTreeWidgetItem(self)
        tables.setText(0, "Tables")

        for (
            table_name,
            table_config,
        ) in self.model_config.tables.get_all().items():
            item = TreeWidgetTable(
                table_name=table_name,
                parent=tables,
                table_dict=table_config,
                model_config=self.model_config,
            )
            item.setText(0, table_name)

        self.items["tables"] = tables

    def _populate_recorders(self) -> None:
        """
        Populates the tree widget with the recorders.
        :return: None
        """
        if self.model_config.recorders is None:
            return

        parent_item = QTreeWidgetItem(self)
        parent_item.setText(0, "Recorders")
        self.items["recorders"] = parent_item

        if not self.model_config.recorders.get_all():
            return

        # get config for all recorders
        for name, config in self.model_config.recorders.get_all().items():
            sub_item = TreeWidgetRecorderName(name=name)
            sub_item.setText(0, name)
            recorder_config_item = TreeWidgetRecorder(
                recorder_config=config,
                model_config=self.model_config,
                parent=sub_item,
            )
            sub_item.addChildren(recorder_config_item.items)
            parent_item.addChild(sub_item)

    def _populate_scenarios(self) -> None:
        """
        Populates the tree widget with the scenarios.
        :return: None
        """
        if not self.model_config.scenarios:
            return

        parent_item = QTreeWidgetItem(self)
        parent_item.setText(0, "Scenarios")

        scenarios = self.model_config.scenarios
        for name in scenarios.names:
            item = QTreeWidgetItem(parent_item)
            item.setText(0, name)
            size = scenarios.get_size_from_name(name)
            if size == 1:
                text = "ensemble"
            else:
                text = "ensembles"
            item.setText(1, f"{scenarios.get_size_from_name(name)} {text}")

        if self.init:
            self.expanded_state.add(parent_item, True)
        else:
            self.expanded_state.store_state(parent_item)

        self.items["scenarios"] = parent_item

    @Slot(QTreeWidgetItem)
    def on_expanded_item(self, item: PySide6.QtWidgets.QTreeWidgetItem) -> None:
        """
        Saves the expanded state for items when user expands an item (by
        double-clicking on it or using the arrow)
        :param item: The expanded item.
        :return: None
        """
        if self.expanded_state.is_state_stored(item):
            self.expanded_state.add(item, False)

    @Slot(QTreeWidgetItem)
    def on_collapse_item(self, item: PySide6.QtWidgets.QTreeWidgetItem) -> None:
        """
        Removes the expanded state for items when user expands an item
        (by double-clicking on it or using the arrow)
        :param item: The collapsed item.
        :return: None
        """
        if self.expanded_state.is_state_stored(item):
            self.expanded_state.remove(item, False)

    @Slot(QTreeWidgetItem)
    def on_item_click(self, clicked_item: QTreeWidgetItem) -> None:
        """
        Slots triggered when an item is clicked.
        :param clicked_item: The item being clicked.
        :return:
        """
        schematic = self.parent.schematic
        schematic.de_select_all_items()

        # center node on the schematic
        if (
            isinstance(clicked_item, TreeWidgetNode)
            and hasattr(clicked_item, "name")
            and clicked_item.name in schematic.schematic_items
        ):
            item = schematic.schematic_items[clicked_item.name]
            item.setSelected(True)
            schematic.center_view_on(item.scenePos())

    @Slot(QAction)
    def on_locate_in_tree(self, node_name: str) -> None:
        """
        Locates the node in tree using its name.
        :param node_name: The node name to locate.
        :return: None
        """
        targets = self.findItems(
            node_name, Qt.MatchExactly | Qt.MatchRecursive, 0
        )
        for t in targets:
            if isinstance(t, TreeWidgetNode):
                # select, expand and scroll to the target node
                t.setSelected(True)
                t.setExpanded(True)
                self.scrollToItem(
                    t, QAbstractItemView.ScrollHint.PositionAtCenter
                )

    @Slot(QPoint)
    def on_context_menu(self, pos: QPoint) -> None:
        """
        Opens the context menu.
        :param pos: The position.
        :return: None
        """
        item = self.itemAt(pos)
        if isinstance(item, TreeWidgetTable):
            table_name = item.name
            context_menu = ContextualMenu()
            context_menu.set_title(table_name)

            # Edit table
            edit_action = context_menu.addAction("Edit")
            # noinspection PyUnresolvedReferences
            edit_action.triggered.connect(
                lambda *args, name=table_name: self.on_edit_table(name)
            )

            # Delete table
            edit_action = context_menu.addAction("Delete...")
            # noinspection PyUnresolvedReferences
            edit_action.triggered.connect(
                lambda *args, name=table_name: self.on_delete_table(name)
            )

            context_menu.exec(self.mapToGlobal(pos))
        elif isinstance(item, TreeWidgetParameterName):
            parameter_name = item.name
            context_menu = ContextualMenu()
            context_menu.set_title(parameter_name)

            # Edit parameter
            edit_action = context_menu.addAction("Edit")
            # noinspection PyUnresolvedReferences
            edit_action.triggered.connect(
                lambda *args, name=parameter_name: self.on_edit_parameter(
                    parameter_name
                )
            )

            # Delete parameter
            edit_action = context_menu.addAction("Delete...")
            # noinspection PyUnresolvedReferences
            edit_action.triggered.connect(
                lambda *args, name=parameter_name: self.on_delete_parameter(
                    parameter_name
                )
            )
            context_menu.exec(self.mapToGlobal(pos))
        elif isinstance(item, TreeWidgetRecorderName):
            recoder_name = item.name
            context_menu = ContextualMenu()
            context_menu.set_title(recoder_name)

            # Edit recorder
            edit_action = context_menu.addAction("Edit")
            # noinspection PyUnresolvedReferences
            edit_action.triggered.connect(
                lambda *args, name=recoder_name: self.on_edit_recorder(
                    recoder_name
                )
            )

            # Delete recorder
            edit_action = context_menu.addAction("Delete...")
            # noinspection PyUnresolvedReferences
            edit_action.triggered.connect(
                lambda *args, name=recoder_name: self.on_delete_recorder(
                    recoder_name
                )
            )

            context_menu.exec(self.mapToGlobal(pos))

    @Slot(str)
    def on_edit_table(self, table_name: str) -> None:
        """
        Opens the dialog to edit the selected table.
        :param table_name: The table name to edit.
        :return: None
        """
        dialog = TablesDialog(
            model_config=self.model_config,
            selected_table_name=table_name,
            parent=self.parent,
        )
        dialog.show()

    @Slot()
    def on_delete_table(self, table_name: str) -> None:
        """
        Deletes the selected table.
        :param table_name: The table name to delete.
        :return: None
        """
        # check if table is being used and warn before deleting
        total_components = self.model_config.tables.is_used(table_name)

        # ask before deleting
        if TablesWidget.maybe_delete(table_name, total_components, self):
            # delete the table from the model configuration
            self.model_config.tables.delete(table_name)
            # update tree and status bar
            self.reload()
            self.parent.statusBar().showMessage(f'Deleted table "{table_name}"')

    @Slot(str)
    def on_edit_parameter(self, parameter_name: str) -> None:
        """
        Opens the dialog to edit the selected parameter.
        :param parameter_name: The parameter name to edit.
        :return: None
        """
        dialog = ParametersDialog(
            model_config=self.model_config,
            selected_parameter_name=parameter_name,
            parent=self.parent,
        )
        dialog.show()

    @Slot()
    def on_delete_parameter(self, parameter_name: str) -> None:
        """
        Deletes the selected parameter.
        :param parameter_name: The parameter name to delete.
        :return: None
        """
        # check if parameter is being used and warn before deleting
        total_components = self.model_config.parameters.is_used(parameter_name)

        # ask before deleting
        if ParametersWidget.maybe_delete(
            parameter_name, total_components, self
        ):
            # delete the parameter from the model configuration
            self.model_config.parameters.delete(parameter_name)
            # update tree and status bar
            self.reload()
            self.parent.statusBar().showMessage(
                f'Deleted parameter "{parameter_name}"'
            )

    @Slot(str)
    def on_edit_recorder(self, recorder_name: str) -> None:
        """
        Opens the dialog to edit the selected recorder.
        :param recorder_name: The recorder name to edit.
        :return: None
        """
        dialog = RecordersDialog(
            model_config=self.model_config,
            selected_recorder_name=recorder_name,
            parent=self.parent,
        )
        dialog.show()

    @Slot()
    def on_delete_recorder(self, recorder_name: str) -> None:
        """
        Deletes the selected parameter.
        :param recorder_name: The recorder name to delete.
        :return: None
        """
        # check if parameter is being used and warn before deleting
        total_components = self.model_config.parameters.is_used(recorder_name)

        # ask before deleting
        if RecordersWidget.maybe_delete(recorder_name, total_components, self):
            # delete the parameter from the model configuration
            self.model_config.parameters.delete(recorder_name)
            # update tree and status bar
            self.reload()
            self.parent.statusBar().showMessage(
                f'Deleted recorder "{recorder_name}"'
            )

    @staticmethod
    def humanise_key(key: str) -> str:
        """
        Returns a human-readable version of a tree key. For example "minimum_version"
        is converted to "Minimum version".
        :param key: The kye to convert.
        :return: The converted string.
        """
        key = str(key).replace("_", " ")
        key = "{}{}".format(key[0].upper(), key[1:])
        return key

    @property
    def stylesheet(self) -> str:
        """
        Returns the stylesheet.
        :return: The stylesheet as string.
        """
        style = {
            "QTreeWidget": {"border": "none"},
            "QTreeWidget::item": {"color": Color("gray", 900).hex},
            "QTreeWidget::item:hover, QTreeWidget::item:selected": {
                "background": "transparent",
            },
            "QTreeWidget::item:selected": {"border": "none"},
            "QTreeWidget::branch:has-siblings:!adjoins-item": {
                "border-image": "url(:components-tree/branch-vline) 0"
            },
            "QTreeWidget::branch:has-siblings:adjoins-item ": {
                "border-image: url(:components-tree/branch-more) 0"
            },
            "QTreeWidget::branch:!has-children:!has-siblings:adjoins-item": {
                "border-image: url(:components-tree/branch-end) 0"
            },
        }
        return stylesheet_dict_to_str(style)


class StyleDelegate(QStyledItemDelegate):
    # noinspection PyUnresolvedReferences
    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionViewItem,
        index: PySide6.QtCore.QModelIndex
        | PySide6.QtCore.QPersistentModelIndex,
    ) -> None:
        """
        Paints the tree item.
        :param painter: The painter instance.
        :param option: The option.
        :param index: The item index.
        :return: None
        """
        super().initStyleOption(option, index)

        # preserve background on item if set
        if (
            option.state & QStyle.State_Selected
            or option.state & QStyle.State_MouseOver
        ):
            if index.data(Qt.ItemDataRole.BackgroundRole) is not None:
                painter.fillRect(
                    option.rect, index.data(Qt.ItemDataRole.BackgroundRole)
                )

        # make fond bold when an item is selected
        if option.state & QStyle.State_Selected:
            option.font.setBold(True)

        super().paint(painter, option, index)
