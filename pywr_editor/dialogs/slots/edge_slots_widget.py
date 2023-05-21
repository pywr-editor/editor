import traceback
from typing import TYPE_CHECKING

from PySide6.QtCore import QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QLineEdit, QVBoxLayout

from pywr_editor.form import FormCustomWidget, FormField
from pywr_editor.model.edges import Edges
from pywr_editor.utils import Logging
from pywr_editor.widgets import TableView

from .edge_slots_model import EdgeSlotsModel

if TYPE_CHECKING:
    from pywr_editor.dialogs import EdgeSlotsDialog


class EdgeSlotsWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: Edges,
        parent: FormField = None,
    ):
        """
        Initialises the widget to show tabled values.
        :param name: The field name.
        :param value: The Edges instance.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget {name} with value {value}")
        super().__init__(name=name, value=value, parent=parent)

        # noinspection PyTypeChecker
        self.dialog: "EdgeSlotsDialog" = self.form.parent
        self.model = EdgeSlotsModel(edges_obj=value, callback=self.on_slot_change)

        # Table
        self.table = TableView(self.model)
        self.table.setMinimumHeight(450)
        self.table.setColumnWidth(0, 240)
        self.table.setColumnWidth(1, 240)

        # Filter names with new model
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(-1)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.sort(-1, Qt.AscendingOrder)
        self.table.setModel(self.proxy_model)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Filter nodes and slots' names")
        # noinspection PyUnresolvedReferences
        self.search_bar.textChanged.connect(self.proxy_model.setFilterFixedString)

        # Set layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.table)

    def on_slot_change(
        self,
        source_node: str,
        target_node: str,
        slot_pos: int,
        slot_name: str | int | None,
        is_multi_split_link: bool,
    ) -> None:
        """
        Updates the slot name when one is changed. This updates the slot in the
        "edges" section if the model and renames the slot in the "slot_names" key
        when the source node is a node inheriting from a MultiSplitLink. If the node
        inherits from MultiSplitLink and slot_name is None an error is throw because
        slot names are mandatory.
        :param source_node: The source node name.
        :param target_node: The target node name.
        :param slot_pos: The position of the slot (1 for the source node, 2 for
        the target node).
        :param slot_name: The slot name.
        :param is_multi_split_link: Whether the source node being change is or inherits
        from MultiSplitLink.
        :return: None
        """
        # update edge
        old_slot_name = self.dialog.model_config.edges.get_slot(
            source_node, target_node, slot_pos
        )
        self.value.set_slot(
            source_node_name=source_node,
            target_node_name=target_node,
            slot_pos=slot_pos,
            slot_name=slot_name,
        )

        # rename slot for node if it is a MultiSplitNode. If the new name or old name
        # is None, the slot position cannot be mapped
        if slot_pos == 1 and old_slot_name and slot_name and is_multi_split_link:
            node_obj = self.dialog.model_config.nodes.config(source_node, as_dict=False)

            # noinspection PyBroadException
            try:
                new_node_dict = node_obj.props
                si = new_node_dict["slot_names"].index(old_slot_name)
                new_node_dict["slot_names"][si] = slot_name
                self.logger.debug(f"Renamed slot for '{source_node}")
                self.dialog.model_config.nodes.update(new_node_dict)
                self.logger.debug(f"New node config is: '{new_node_dict}")
            except Exception:
                self.logger.debug(f"Renaming skipped because: '{traceback.print_exc()}")
                pass

        # update tree and status bar
        app = self.dialog.app
        if app is not None:
            action = "Changed" if slot_name is not None else "Removed"
            if hasattr(app, "components_tree"):
                app.components_tree.reload()
            if hasattr(app, "statusBar"):
                app.statusBar().showMessage(
                    f"{action} slot for edge {source_node}-{target_node}"
                )

    def get_value(self) -> None:
        """
        This widget does not return any value.
        :return: None
        """
        return None
