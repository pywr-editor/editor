import json

from PySide6.QtCore import QFile, QTextStream

"""
 Utility class for pywr data.
"""


class PywrData:
    def __init__(self, suffix: str, resource_name: str):
        """
        Loads the resource with the components' data.
        :param suffix: The suffix of the pywr component (for example parameter or
        recorder).
        :param resource_name: The name of the resource containing the data for the
        component. The resource must contain a dictionary with the "key_lookup" and
        "data" keys.
        """
        file = QFile(resource_name)
        file.open(QFile.ReadOnly | QFile.Text)
        components_data: dict = json.loads(QTextStream(file).readAll())
        file.close()

        self.suffix = suffix
        self.key_lookup: dict = components_data["key_lookup"]
        # sort keys alphabetically
        self.data = dict(sorted(components_data["data"].items()))

    def lookup_key(self, component_type: str) -> str | None:
        """
        Return the lookup key of the data dictionary from a component type.
        :param component_type: The string identifying the component type.
        :return: The component lookup key.
        """
        if component_type.lower() in self.key_lookup.keys():
            return self.key_lookup[component_type.lower()]
        return None

    def name(self, component_type: str) -> str | None:
        """
        Return the component name from the component type.
        :param component_type: The string identifying the component type.
        :return: The pywr component name.
        """
        data_key = self.lookup_key(component_type)
        if data_key is None:
            return None
        return self.data[data_key]["name"]

    @property
    def names(self) -> list[str]:
        """
        Return a list of the pywr components' names.
        :return: The pywr components' names
        """
        return [component_info["name"] for component_info in self.data.values()]

    @property
    def classes(self) -> list[str]:
        """
        Return a list of the pywr components' classes.
        :return: The pywr component classes
        """
        return [component_info["class"] for component_info in self.data.values()]

    @property
    def keys(self) -> list[str]:
        """
        Return a list of the available pywr keys for the components.
        :return: The component's keys.
        """
        return list(self.key_lookup.keys())

    @property
    def values(self) -> list[str]:
        """
        Return a list of the available pywr name variations for the components.
        :return: The component's name variations.
        """
        return list(self.key_lookup.values())

    def info_from_type_(self, component_type: str, info_key: str) -> str | None:
        """
        Return the component information (class, url, etc.) from the component type.
        :param component_type: The string identifying the component type.
        :param info_key: The key in the information dictionary.
        :return: The component information, if found. None otherwise.
        """
        if component_type is None:
            return None

        data_key = self.lookup_key(component_type)
        if data_key is not None and info_key in self.data[data_key]:
            return self.data[data_key][info_key]
        return None

    def exists(self, component_type: str) -> bool:
        """
        Returns True if the component type exists.
        :param component_type: The string identifying the component type.
        :return: True if the component key type, False otherwise.
        """
        return self.lookup_key(component_type) is not None

    def class_from_type(self, component_type: str) -> str | None:
        """
        Return the pywr class from the component type.
        :param component_type: The string identifying the component type.
        :return: The pywr component class, if found. None otherwise.
        """
        return self.info_from_type_(component_type, "class")

    def doc_url(self, component_type: str) -> str | None:
        """
        Return the URl to the pywr documentation from the component type.
        :param component_type: The string identifying the component type.
        :return: The URL to the documentation. None otherwise.
        """
        return self.info_from_type_(component_type, "doc_url")

    def keys_with_parent_class(
        self, subclass_name: str, include_parent: bool = True
    ) -> list[str]:
        """
        Return the component keys with a parent class matching the provided name.
        :param subclass_name: The name of the component parent class, for example
        IndexParameter.
        :param include_parent: Whether to return the key of the parent class too.
        Default to True.
        :return: A list of pywr component keys.
        """
        keys = []
        # store the key of the parent class too
        if include_parent and subclass_name.lower() in self.keys:
            keys.append(self.key_lookup[subclass_name.lower()])

        for key, data in self.data.items():
            if subclass_name in data["sub_classes"]:
                keys.append(key)

        return keys

    def humanise_name(self, component_type: str) -> str | None:
        """
        Replace a component name with a human-readable string. For example
        "BinaryStepParameter" is converted to "Binary step component". Custom component
        names are not renamed.
        :param component_type: The string identifying the component type.
        :return: The formatted component name.
        """
        if component_type is None:
            return None

        data_key = self.lookup_key(component_type)
        if data_key is not None:
            if self.suffix:
                return self.data[data_key]["name"].replace(f" {self.suffix}", "")
            else:
                return self.data[data_key]["name"]
        return component_type

    def is_custom(self, component_type: str) -> bool:
        """
        Return True if the component is not a built-in pywr component.
        :param component_type: The string identifying the component type.
        :return: True if the component is custom, False otherwise.
        """
        return not self.exists(component_type)
