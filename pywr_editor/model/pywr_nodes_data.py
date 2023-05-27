import json

from PySide6.QtCore import QFile, QTextStream

"""
 Utility class for pywr built-in nodes.
"""


class PywrNodesData:
    def __init__(self):
        """
        Utility class to get the available pywr nodes and their information.
        """
        file = QFile(":model/node-data")
        file.open(QFile.ReadOnly | QFile.Text)

        self.nodes_data: dict = json.loads(QTextStream(file).readAll())

    def name(self, node_type: str) -> str | None:
        """
        Returns the node name from the node type.
        :param node_type: The string identifying the node type.
        :return: The pywr node name.
        """
        node_type = node_type.lower()
        if node_type not in self.nodes_data.keys():
            return None
        return self.nodes_data[node_type]["name"]

    @property
    def names(self) -> list[str]:
        """
        Returns a list of the pywr nodes' names.
        :return: The nodes' names.
        """
        return [node_info["name"] for node_info in self.nodes_data.values()]

    @property
    def classes(self) -> list[str]:
        """
        Returns a list of the pywr nodes' classes.
        :return: The pywr nodes classes
        """
        return [node_info["class"] for node_info in self.nodes_data.values()]

    @property
    def keys(self) -> list[str]:
        """
        Returns the pywr nodes' keys.
        :return: The nodes' keys.
        """
        return list(self.nodes_data.keys())

    def does_type_exist(self, node_type: str) -> bool:
        """
        Returns True if the node type exists in the available node keys (i.e. the
        lowercase node classes; for example aggregatednode for AggregatedNode).
        :param node_type: The string identifying the node type.
        :return: True if the node key type, False otherwise.
        """
        node_type = node_type.lower()
        return node_type in self.keys

    def is_custom(self, node_type: str) -> bool:
        """
        Return True if the node is not a built-in pywr node.
        :param node_type: The string identifying the node type.
        :return: True if the node is custom, False otherwise.
        """
        return not self.does_type_exist(node_type)

    def keys_with_parent_class(
        self, subclass_name: str, include_parent: bool = True
    ) -> list[str]:
        """
        Return the node keys whose parent class matches parent_class_name.
        :param subclass_name: The name of the parent class, for example Reservoir.
        :param include_parent: Whether to return the key of the parent class too.
        Default to True.
        :return: A list of pywr node keys.
        """
        keys = []
        # store the key of the parent class too
        if include_parent:
            keys.append(subclass_name.lower())

        for key, data in self.nodes_data.items():
            if subclass_name in data["sub_classes"]:
                keys.append(key)
        return keys

    def class_from_type(self, node_type: str | None) -> str | None:
        """
        Returns the pywr class from the node type.
        :param node_type: The string identifying the node type.
        :return: The pywr node class, if found. None otherwise.
        """
        if node_type and node_type.lower() in self.keys:
            return self.nodes_data[node_type]["class"]
        return None

    def humanise_name(self, node_type: str) -> str | None:
        """
        Replaces a node type with a human-readable string. For example
        "AggregatedNode" is converted to "Aggregated node". Custom parameter
        names are not renamed.
        :param node_type: The string identifying the node type.
        :return: The formatted node name.
        """
        if node_type is None:
            return None
        if node_type in self.nodes_data:
            return self.nodes_data[node_type]["name"]
        return node_type
