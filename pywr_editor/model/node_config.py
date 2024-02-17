from copy import deepcopy as dp
from typing import Sequence

from pywr_editor.model import ComponentConfig, Constants, PywrNodesData

"""
 Handles the model node configuration
"""


class NodeConfig(ComponentConfig):
    def __init__(self, props: dict = None, deepcopy: bool = False):
        """
        Initialise the class.
        :param props: The node dictionary.
        :param deepcopy: Whether to create a deepcopy of the dictionary. Default to
        False.
        """
        super().__init__(props=props)

        self.custom_node_group_name = Constants.CUSTOM_NODE_GROUP_NAME.value
        if deepcopy is True:
            self.props = dp(self.props)

    @property
    def name(self) -> str | None:
        """
        Return the node name.
        :return: The name of the node
        """
        return self.props["name"]

    @property
    def custom_style(self) -> str | None:
        """
        Return the custom node style.
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
        Return the color name to use for the edge.
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
        Return the node position.
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
        Return the node position.
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

    def change_name(self, name: str) -> None:
        """
        Change the node name.
        :param name: The new name.
        :return: None. This only update the internal dictionary.
        """
        self.props["name"] = name

    def change_position(self, position: list[float]) -> None:
        """
        Change the node position.
        :param position: The new position to set.
        :return: None. This only update the internal dictionary.
        """
        position_key = Constants.POSITION_KEY.value
        if "position" in self.props:
            self.props["position"][position_key] = position
        else:
            self.props["position"] = {position_key: position}

    @property
    def is_visible(self) -> bool:
        """
        Return True if the node is visible on the schematic.
        :return: True if the node is visible, False otherwise.
        """
        if "visible" not in self.props or not isinstance(self.props["visible"], bool):
            return True

        return self.props["visible"]

    @property
    def is_virtual(self) -> bool:
        """
        Check if a node is virtual (i.e. the node is not connectable).
        :return: True if the node is virtual, False otherwise
        """
        return self.key in [
            "annualvirtualstorage",
            "virtualstorage",
            "aggregatednode",
            "aggregatedstorage",
            "seasonalvirtualstorage",
        ]

    @property
    def humanised_type(self) -> str:
        """
        Return a user-friendly string identifying the type of node.
        :return The node type.
        """
        pywr_nodes = PywrNodesData()
        if pywr_nodes.exists(self.type):
            return pywr_nodes.name(self.type)
        else:
            return self.custom_node_group_name

    @staticmethod
    def create(name: str, node_type: str, position: Sequence[float]) -> dict:
        """
        Create a new dictionary with the node properties.
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
