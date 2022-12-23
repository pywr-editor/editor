import json

from PySide6.QtCore import QFile, QTextStream

"""
 Utility class for pywr built-in recorders.
"""


class PywrRecordersData:
    def __init__(self):
        """
        Opens the resource file containing the recorder's information.
        """
        file = QFile(":model/recorder-data")
        file.open(QFile.ReadOnly | QFile.Text)
        all_data = json.loads(QTextStream(file).readAll())

        self.key_lookup: dict = all_data["recorders_key_lookup"]
        # sort keys alphabetically
        self.recorders = dict(sorted(all_data["recorders_data"].items()))

    def get_lookup_key(self, recorder_type: str) -> str | None:
        """
        Returns the lookup key of the data dictionary from a recorder type.
        :param recorder_type: The string identifying the recorder type.
        :return: The recorder data key.
        """
        if recorder_type.lower() in self.key_lookup.keys():
            return self.key_lookup[recorder_type.lower()]
        return None

    def name(self, recorder_type: str) -> str | None:
        """
        Returns the recorder name from the recorder key.
        :param recorder_type: The string identifying the recorder type.
        :return: The pywr recorder name.
        """
        data_key = self.get_lookup_key(recorder_type)
        if data_key is None:
            return None
        return self.recorders[data_key]["name"]

    @property
    def names(self) -> list[str]:
        """
        Returns a list of the pywr recorders' names.
        :return: The pywr recorders' names
        """
        return [
            recorder_info["name"] for recorder_info in self.recorders.values()
        ]

    @property
    def classes(self) -> list[str]:
        """
        Returns a list of the pywr recorder' classes.
        :return: The pywr recorder classes
        """
        return [
            recorder_info["class"] for recorder_info in self.recorders.values()
        ]

    @property
    def keys(self) -> list[str]:
        """
        Returns a list of the available pywr classes for the recorder.
        :return: The recorder's keys.
        """
        return list(self.key_lookup.keys())

    def get_class_from_type(self, recorder_type: str) -> str | None:
        """
        Returns the pywr class from the recorder key.
        :param recorder_type: The string identifying the recorder type.
        :return: The pywr recorder class, if found. None otherwise.
        """
        return self.get_info_from_type(recorder_type, "class")

    def get_info_from_type(
        self, recorder_type: str, info_key: str
    ) -> str | None:
        """
        Returns the recorder information (class, url, etc.) from the recorder type.
        :param recorder_type: The string identifying the recorder type.
        :param info_key: The key in the information dictionary.
        :return: The recorder information, if found. None otherwise.
        """
        if recorder_type is None:
            return None

        data_key = self.get_lookup_key(recorder_type)
        if data_key is not None and info_key in self.recorders[data_key]:
            return self.recorders[data_key][info_key]
        return None

    def humanise_name(self, recorder_type: str) -> str | None:
        """
        Replaces a recorder name with a human-readable string. For example
        "NumpyArrayParameterRecorder" is converted to
        "Numpy array parameter recorder". Custom recorder names are not renamed.
        :param recorder_type: The string identifying the recorder type.
        :return: The formatted recorder name.
        """
        if recorder_type is None:
            return None

        data_key = self.get_lookup_key(recorder_type)
        if data_key is not None:
            return self.recorders[data_key]["name"].replace(" recorder", "")
        return recorder_type

    def get_doc_url_from_key(self, recorder_type: str) -> str | None:
        """
        Returns the URl to the pywr documentation from the recorder type.
        :param recorder_type: The string identifying the recorder type.
        :return: The URL to the documentation. None otherwise.
        """
        return self.get_info_from_type(recorder_type, "doc_url")

    def get_keys_with_parent_class(
        self, subclass_name: str, include_parent: bool = False
    ) -> list[str]:
        """
        Returns the recorder keys with a parent class matching the provided name.
        :param subclass_name: The name of the recorder parent class, for example
        EventRecorder.
        :param include_parent: Whether to return the key of the parent class too.
        :return: A list of pywr recorder keys.
        """
        keys = []
        # store the key of the parent class too
        if include_parent:
            keys.append(self.key_lookup[subclass_name.lower()])

        for key, data in self.recorders.items():
            if subclass_name in data["sub_classes"]:
                keys.append(key)

        return keys
