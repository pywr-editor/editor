from dataclasses import dataclass
from pywr_editor.model import NodeConfig, JsonUtils, DictMatches, Constants
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig

"""
 Handle the model nodes.
"""


@dataclass
class Nodes:
    model: "ModelConfig"
    """ The ModelConfig instance """

    def get_all(self) -> list[dict]:
        """
        Returns the list of the nodes.
        :return: The node list. Each list item contains the node properties as
        dictionary.
        """
        if "nodes" in self.model.json:
            return self.model.json["nodes"]
        return []

    @property
    def names(self) -> list[str]:
        """
        Returns the list of the node names.
        :return: The node name list.
        """
        return [node["name"] for node in self.get_all()]

    @property
    def count(self) -> int:
        """
        Returns the total number of nodes.
        :return: The nodes count.
        """
        return len(self.get_all())

    @staticmethod
    def node(node_dict: dict, deepcopy: bool = False) -> NodeConfig:
        """
        Returns the NodeConfig instance.
        :param node_dict: The node dictionary.
        :param deepcopy: Whether to create a deepcopy of the node dictionary.
        Default to False.
        :return: The NodeConfig instance
        """
        return NodeConfig(node_dict, deepcopy)

    def set_position(
        self,
        position: list[float],
        node_name: str | None = None,
        node_index: int | None = None,
    ) -> dict:
        """
        Sets or updates the editor position of a node identified by its name or index.
        :param position: The position to set as list.
        :param node_name: The name of the node.
        :param node_index: The index of the node.
        :return: The updated node dictionary.
        """
        if node_name is None and node_index is None:
            raise ValueError(
                "You must provide a node name or index to update its position"
            )

        if node_name is not None:
            node_index = self.find_node_index_by_name(node_name)
        else:
            node_name = self.model.json["nodes"][node_index]["name"]

        editor_position_key = Constants.POSITION_KEY.value
        if "position" in self.model.json["nodes"][node_index]:
            self.model.json["nodes"][node_index]["position"][
                editor_position_key
            ] = position
        else:
            self.model.json["nodes"][node_index]["position"] = {
                editor_position_key: position
            }

        self.model.changes_tracker.add(
            f'Changed node position for node "{node_name}" to {position}'
        )
        return self.model.json["nodes"][node_index]

    def set_pywr_position(
        self,
        position: list[float],
        node_name: str | None = None,
        node_index: int | None = None,
    ) -> None:
        """
        Sets or updates the pywr position of a node.
        :param position: The position to set as list.
        :param node_name: The name of the node.
        :param node_index: The index of the node.
        :return: None
        """
        if node_name is None and node_index is None:
            raise ValueError(
                "You must provide a node name or index to update its position"
            )

        if node_name is not None:
            node_index = self.find_node_index_by_name(node_name)
        else:
            node_name = self.model.json["nodes"][node_index]["name"]

        if "position" in self.model.json["nodes"][node_index]:
            self.model.json["nodes"][node_index]["position"][
                "schematic"
            ] = position
        else:
            self.model.json["nodes"][node_index]["position"] = {
                "schematic": position
            }

        self.model.changes_tracker.add(
            f'Changed node position for node "{node_name}" to {position}'
        )

    def find_node_index_by_name(self, node_name: str) -> int | None:
        """
        Finds the node index in the list by the node name.
        :param node_name: The node to look for.
        :return: The node index if the name is found. None otherwise.
        """
        return next(
            (
                idx
                for idx, node in enumerate(self.get_all())
                if node["name"] == node_name
            ),
            None,
        )

    def get_node_config_from_name(
        self, node_name: str, as_dict: bool = True
    ) -> dict | NodeConfig | None:
        """
        Finds the node configuration dictionary by the node name.
        :param node_name: The node to look for.
        :param as_dict: Returns the configuration as dictionary when True, the
        NodeConfig instance if False.
        :return: The node configuration if found, None otherwise.
        """
        node_idx = self.find_node_index_by_name(node_name)
        if node_idx is not None:
            node_dict = self.get_all()[node_idx]
            if as_dict:
                return node_dict
            else:
                return NodeConfig(props=node_dict)
        return None

    def delete(self, node_name: str) -> None:
        """
        Deletes a node and its edges from the model dictionary.
        :param node_name: The node name to delete.
        :return: None
        """
        node_idx = self.find_node_index_by_name(node_name)
        if node_idx is not None:
            del self.model.json["nodes"][node_idx]
            self.model.changes_tracker.add(f'Deleted node named "{node_name}"')
            self.model.edges.delete(source_node_name=node_name)
            self.model.edges.delete(target_node_name=node_name)

    def find_orphans(self) -> list[str] | None:
        """
        Finds orphaned nodes.
        :return: A list of orphaned node names or None if there are not any.
        """
        nodes_in_edges = set()
        for edge in self.model.edges.get_all():
            nodes_in_edges = nodes_in_edges.union(set(edge))

        orphaned_node_names = []
        for node_dict in self.get_all():
            node_config = self.node(node_dict)
            if (
                not node_config.is_virtual
                and node_config.name not in nodes_in_edges
            ):
                orphaned_node_names.append(node_config.name)

        if len(orphaned_node_names) > 0:
            return orphaned_node_names
        return None

    def add(self, node_config: dict) -> None:
        """
        Adds a new node to the model.
        :param node_config: The configuration dictionary.
        :return: None
        """
        node_keys = node_config.keys()
        if "name" not in node_keys or "type" not in node_keys:
            raise KeyError(
                "The node configuration must have a name and a type set"
            )

        self.model.json["nodes"].append(node_config)
        self.model.changes_tracker.add(
            f"Added new node with the following properties: {node_config}"
        )

    def update(self, node_dict: dict) -> None:
        """
        Replaces the node dictionary for an existing node. This preserves the
        node position.
        :param node_dict: The node dictionary with the fields to update.
        :return: None
        """
        if "name" not in node_dict:
            raise ValueError("The node must have a name")

        node_name = node_dict["name"]
        node_index = self.find_node_index_by_name(node_name)
        node_obj: NodeConfig = self.get_node_config_from_name(
            node_name=node_name, as_dict=False
        )
        if node_obj is None:
            return

        new_node_dict = {"position": {}}

        # preserve the positions and the color key
        if node_obj.pywr_position is not None:
            new_node_dict["position"]["schematic"] = node_obj.pywr_position
        if node_obj.position is not None:
            new_node_dict["position"][
                Constants.POSITION_KEY.value
            ] = node_obj.position
        if "color" in node_obj.props:
            new_node_dict["color"] = node_obj.props["color"]

        # move the edge color and node style values
        edge_color_key = Constants.EDGE_COLOR_KEY.value
        if edge_color_key in node_dict:
            new_node_dict["position"][edge_color_key] = node_dict[
                edge_color_key
            ]
            del node_dict[edge_color_key]
        node_style_key = Constants.NODE_STYLE_KEY.value
        if node_style_key in node_dict:
            new_node_dict["position"][node_style_key] = node_dict[
                node_style_key
            ]
            del node_dict[node_style_key]

        # drop position key if empty
        if len(new_node_dict["position"]) == 0:
            del new_node_dict["position"]

        new_node_dict = {**node_dict, **new_node_dict}
        self.model.json["nodes"][node_index] = new_node_dict
        self.model.changes_tracker.add(
            f"Updated node at index '{node_index}' with the following values:"
            + f" {new_node_dict}"
        )

    def find_dependencies(self, node_name: str) -> DictMatches | None:
        """
        Checks the model components using the node name.
        :param node_name: The name of the node.
        :return: The occurrence and model components using the node.
        If the node does not exist, this returns None.
        """
        if self.find_node_index_by_name(node_name) is None:
            return None

        dict_utils = JsonUtils(self.model.json).find_str(string=node_name)
        # remove the occurrence of the name in the "nodes" key
        if dict_utils.occurrences > 0:
            dict_utils.paths = dict_utils.paths[1:]
            dict_utils.occurrences -= 1

        return dict_utils

    def rename(self, node_name: str, new_name: str) -> None:
        """
        Renames a node. This changes the name in the "name" dictionary key
        in each model component, where the node is referred.
        :param node_name: The node name to change.
        :param new_name: The new node name.
        :return: None
        """
        node_index = self.find_node_index_by_name(node_name)
        if node_index is None:
            return None

        # rename key in node dictionary
        self.model.json["nodes"][node_index]["name"] = new_name

        # rename references in edges
        self.model.json["edges"] = JsonUtils(
            self.model.json["edges"]
        ).replace_str(
            old=node_name,
            new=new_name,
        )

        # rename references in model components
        self.model.json = JsonUtils(self.model.json).replace_str(
            old=node_name,
            new=new_name,
            match_key=[
                # keys used by parameters and recorders
                "node",
                "nodes",
                "storage_node",
                "storage_nodes",
            ],
        )
        self.model.changes_tracker.add(
            f"Change node name from {node_name} to " + f"{new_name}"
        )
