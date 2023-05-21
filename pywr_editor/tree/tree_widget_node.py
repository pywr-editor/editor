from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QTreeWidgetItem

from pywr_editor.model import ModelConfig
from pywr_editor.widgets import ParameterIcon

from .abstract_tree_widget_component import AbstractTreeWidgetComponent
from .tree_widget_parameter import TreeWidgetParameter


class TreeWidgetNodeAttribute(QTreeWidgetItem):
    def __init__(self, parent=None):
        super().__init__(parent)


class TreeWidgetNode(QTreeWidgetItem):
    def __init__(self, node_dict: dict, model_config: ModelConfig):
        """
        Initialises the item containing the node name and its attributes.
        :param node_dict: The node properties.
        :param model_config: The ModelConfig instance.
        """
        super().__init__()
        # self.node_dict = node_dict
        self.model_config = model_config
        self.node_obj = self.model_config.nodes.node(node_dict, deepcopy=True)
        self.node_dict = self.node_obj.props

        # main props
        self.type = self.node_obj.type
        self.name = self.node_obj.name

        node_tooltip = self.name
        if self.node_obj.is_virtual:
            node_tooltip = f"{node_tooltip} (Virtual)"
        self.setText(0, self.name)
        self.setToolTip(0, node_tooltip)
        self.sortChildren(0, Qt.SortOrder.AscendingOrder)

        # remove unused keys
        self.node_obj.delete_attribute(
            ["name", "type", "color", "position", "show_label"]
        )

        self.addChildren(self.children)

    @property
    def children(self) -> list[QTreeWidgetItem]:
        """
        Collects the node's attributes.
        :return: A list of items.
        """
        items = []
        for attribute_name, attribute_value in self.node_dict.items():
            prop_list = attribute_name.split("_")
            prop_list[0] = prop_list[0].title()

            item = TreeWidgetNodeAttribute()
            # do not rename attributes for custom nodes
            if self.model_config.pywr_node_data.is_custom_node(self.type):
                item.setText(0, attribute_name)
            else:
                item.setText(0, self.node_obj.humanise_attribute_name(attribute_name))
            items.append(item)

            if isinstance(attribute_value, dict):
                parameter_items = TreeWidgetParameter(
                    parameter_config=attribute_value,
                    model_config=self.model_config,
                    parent=item,
                )
                item.addChildren(parameter_items.items)
            # nodes and any other key that does not provide a parameter
            # (for example for AggregatedNode.nodes)
            elif isinstance(attribute_value, list):
                parameter_items = AbstractTreeWidgetComponent(
                    comp_value=attribute_value,
                    model_config=self.model_config,
                    parent_type=list,
                    parent=item,
                )
                item.addChildren(parameter_items.items)
            # constant parameter or string
            else:
                item.setText(1, str(attribute_value))
                if isinstance(attribute_value, str):
                    item.setToolTip(1, attribute_value)
                    tooltip = attribute_value

                    param_obj = self.model_config.parameters.config(
                        attribute_value, False
                    )
                    if param_obj is not None and param_obj.is_a_model_parameter:
                        icon_key = param_obj.type
                        tooltip = f"{tooltip} ({param_obj.humanised_type})"
                        item.setIcon(1, QIcon(ParameterIcon(icon_key)))
                    item.setToolTip(1, tooltip)

        return items
