from copy import deepcopy as dp
from typing import Sequence

from pywr_editor.model import Constants, PywrNodesData

"""
 Handles the model node configuration.
"""


class NodeConfig:
    def __init__(self, props: dict, deepcopy: bool = False):
        """
        Initialises the class.
        :param props: The node dictionary.
        :param deepcopy: Whether to create a deepcopy of the dictionary. Default to
        False.
        """
        self.props = props
        self.custom_node_group_name = Constants.CUSTOM_NODE_GROUP_NAME.value

        if deepcopy is True:
            self.props = dp(self.props)

    @property
    def type(self) -> str:
        """
        Returns the node type.
        :return: The type of the node
        """
        return self.string_to_key(self.props["type"])

    @property
    def name(self) -> str | None:
        """
        Returns the node name.
        :return: The name of the node
        """
        return self.props["name"]

    @property
    def custom_style(self) -> str | None:
        """
        Returns the custom node style.
        :return: The node style or None if this is not set.
        """
        node_style_key = Constants.NODE_STYLE_KEY.value
        if (
            "position" not in self.props
            or node_style_key not in self.props["position"]
            or not isinstance(self.props["position"][node_style_key], str)
        ):
            return None

        return self.props["position"][node_style_key].lower()

    @property
    def edge_color(self) -> str | None:
        """
        Returns the color name to use for the edge.
        :return: The edge_color property or None if this is not set.
        """
        edge_color_key = Constants.EDGE_COLOR_KEY.value
        if (
            "position" not in self.props
            or edge_color_key not in self.props["position"]
            or not isinstance(self.props["position"][edge_color_key], str)
        ):
            return None

        return self.props["position"][edge_color_key]

    @property
    def pywr_position(self) -> list[float] | None:
        """
        Returns the node position.
        :return: The node position if available, None otherwise.
        """
        if (
            "position" in self.props
            and "schematic" in self.props["position"]
            and isinstance(self.props["position"]["schematic"], list)
        ):
            return self.props["position"]["schematic"]
        return None

    @property
    def position(self) -> list[float | int] | None:
        """
        Returns the node position.
        :return: The node position if available, None otherwise.
        """
        position_key = Constants.POSITION_KEY.value
        if (
            "position" in self.props
            and position_key in self.props["position"]
            and isinstance(self.props["position"][position_key], (list, tuple))
            and len(self.props["position"][position_key]) == 2
        ):
            return self.props["position"][position_key]
        return None

    @property
    def is_visible(self) -> bool:
        """
        Returns True if the node is visible on the schematic.
        :return: True if the node is visible, False otherwise.
        """
        if "visible" not in self.props or not isinstance(
            self.props["visible"], bool
        ):
            return True

        return self.props["visible"]

    @property
    def is_virtual(self) -> bool:
        """
        Checks if a node is virtual (i.e. the node is not connectable).
        :return: True if the node is virtual, False otherwise
        """
        return self.type in [
            "annualvirtualstorage",
            "virtualstorage",
            "aggregatednode",
            "aggregatedstorage",
            "seasonalvirtualstorage",
        ]

    def delete_attribute(self, attribute: str | list) -> None:
        """
        Deletes an attribute or a list of attributes in the node's dictionary.
        :param attribute: The attribute or attributes to remove.
        :return: None
        """
        if isinstance(attribute, str):
            if attribute in self.props:
                del self.props[attribute]
        elif isinstance(attribute, list):
            for attr in attribute:
                if attr in self.props:
                    del self.props[attr]

    @property
    def humanised_type(self) -> str:
        """
        Returns a user-friendly string identifying the type of node.
        :return The node type.
        """
        pywr_nodes = PywrNodesData()
        if pywr_nodes.does_type_exist(self.type):
            return pywr_nodes.name(self.type)
        else:
            return self.custom_node_group_name

    @staticmethod
    def humanise_attribute_name(attribute_name: str) -> str | None:
        """
        Renames an attribute name. For example max_flow is converted to "Max flow".
        :param attribute_name: The attribute to convert.
        :return: The converted attribute.
        """
        if attribute_name is None:
            return None
        elif attribute_name == "type":
            return attribute_name
        elif attribute_name == "mrf":
            return "Minimum residual flow"
        elif attribute_name == "mrf_cost":
            return "Minimum residual flow cost"
        elif attribute_name == "initial_volume_pc":
            return "Initial volume (%)"

        prop_list = attribute_name.split("_")
        prop_list[0] = prop_list[0].title()
        return " ".join(prop_list)

    @staticmethod
    def create(name: str, node_type: str, position: Sequence[float]) -> dict:
        """
        Creates a new dictionary with the node properties.
        :param name: The node name.
        :param node_type: The node type.
        :param position: The node position.
        :return: A dictionary with the basic node properties.
        """
        return {
            "name": name,
            "type": node_type,
            "position": {
                Constants.POSITION_KEY.value: [
                    round(position[0], 4),
                    round(position[1], 4),
                ]
            },
        }

    @staticmethod
    def string_to_key(node_class: str | None) -> str | None:
        """
        Converts the node class or type (the string in the dictionary "type" key)
        to a node key (i.e. lower case string).
        :param node_class: The node class or type.
        :return: The node key.
        """
        if not node_class:
            return None
        return node_class.lower()
