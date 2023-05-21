import json

from PySide6.QtCore import QFile, QTextStream

"""
 Utility class for pywr built-in parameters.
"""


class PywrParametersData:
    def __init__(self):
        """
        Loads the resource with the parameters' data
        """
        file = QFile(":model/parameter-data")
        file.open(QFile.ReadOnly | QFile.Text)
        parameters_data: dict = json.loads(QTextStream(file).readAll())
        file.close()

        self.key_lookup: dict = parameters_data["parameters_key_lookup"]
        # sort keys alphabetically
        self.parameters = dict(sorted(parameters_data["parameters_data"].items()))

    def get_lookup_key(self, parameter_type: str) -> str | None:
        """
        Returns the lookup key of the data dictionary from a parameter type.
        :param parameter_type: The string identifying the parameter type.
        :return: The parameter lookup key.
        """
        if parameter_type.lower() in self.key_lookup.keys():
            return self.key_lookup[parameter_type.lower()]
        return None

    def name(self, parameter_type: str) -> str | None:
        """
        Returns the parameter name from the parameter type.
        :param parameter_type: The string identifying the parameter type..
        :return: The pywr parameter name.
        """
        data_key = self.get_lookup_key(parameter_type)
        if data_key is None:
            return None
        return self.parameters[data_key]["name"]

    @property
    def names(self) -> list[str]:
        """
        Returns a list of the pywr parameters' names.
        :return: The pywr parameters' names
        """
        return [parameter_info["name"] for parameter_info in self.parameters.values()]

    @property
    def classes(self) -> list[str]:
        """
        Returns a list of the pywr parameters' classes.
        :return: The pywr parameter classes
        """
        return [parameter_info["class"] for parameter_info in self.parameters.values()]

    @property
    def keys(self) -> list[str]:
        """
        Returns a list of the available pywr keys for the parameters.
        :return: The parameter's keys.
        """
        return list(self.key_lookup.keys())

    @property
    def values(self) -> list[str]:
        """
        Returns a list of the available pywr name variations for the parameters.
        :return: The parameter's name variations.
        """
        return list(self.key_lookup.values())

    def get_info_from_type(self, parameter_type: str, info_key: str) -> str | None:
        """
        Returns the parameter information (class, url, etc.) from the parameter type.
        :param parameter_type: The string identifying the parameter type.
        :param info_key: The key in the information dictionary.
        :return: The parameter information, if found. None otherwise.
        """
        if parameter_type is None:
            return None

        data_key = self.get_lookup_key(parameter_type)
        if data_key is not None and info_key in self.parameters[data_key]:
            return self.parameters[data_key][info_key]
        return None

    def get_class_from_type(self, parameter_type: str) -> str | None:
        """
        Returns the pywr class from the parameter type.
        :param parameter_type: The string identifying the parameter type.
        :return: The pywr parameter class, if found. None otherwise.
        """
        return self.get_info_from_type(parameter_type, "class")

    def get_doc_url_from_key(self, parameter_type: str) -> str | None:
        """
        Returns the URl to the pywr documentation from the parameter type.
        :param parameter_type: The string identifying the parameter type.
        :return: The URL to the documentation. None otherwise.
        """
        return self.get_info_from_type(parameter_type, "doc_url")

    def get_keys_with_parent_class(
        self, subclass_name: str, include_parent: bool = False
    ) -> list[str]:
        """
        Returns the parameter keys with a parent class matching the provided name.
        :param subclass_name: The name of the parameter parent class, for example
        IndexParameter.
        :param include_parent: Whether to return the key of the parent class too.
        :return: A list of pywr parameter keys.
        """
        keys = []
        # store the key of the parent class too
        if include_parent:
            keys.append(self.key_lookup[subclass_name.lower()])

        for key, data in self.parameters.items():
            if subclass_name in data["sub_classes"]:
                keys.append(key)

        return keys

    def humanise_name(self, parameter_type: str) -> str | None:
        """
        Replaces a parameter name with a human-readable string. For example
        "BinaryStepParameter" is converted to "Binary step parameter". Custom parameter
        names are not renamed.
        :param parameter_type: The string identifying the parameter type.
        :return: The formatted parameter name.
        """
        if parameter_type is None:
            return None

        data_key = self.get_lookup_key(parameter_type)
        if data_key is not None:
            return self.parameters[data_key]["name"].replace(" parameter", "")
        return parameter_type
