from copy import deepcopy as dp

from pywr_editor.model import PywrRecordersData

"""
 Handles a recorder.
"""


class RecorderConfig:
    def __init__(
        self,
        props: dict,
        name: str | None = None,
        model_recorder_names: list | None = None,
        deepcopy: bool = False,
    ):
        """
        Initialises the class.
        :param props: The recorder configuration.
        :param model_recorder_names: The list of recorder names in the "recorders"
        model section of the JSON dictionary.
        :param name: The recorder's name if available. Anonymous recorders (i.e.
        those nested in a node or a parameter) have no name.
        :param deepcopy: Whether to create a deepcopy of the dictionary.
        """
        self.props = props
        if not isinstance(self.props, dict):
            self.props = {}
        if deepcopy:
            self.props = dp(self.props)

        self.model_recorder_names = model_recorder_names
        self.name = name
        if not isinstance(self.name, str):
            self.name = None

    @property
    def type(self) -> str | None:
        """
        Returns the recorder type. For custom parameters, this is the name.
        :return: The type of the recorder.
        """
        if "type" in self.props and self.props["type"]:
            return self.props["type"]
        return None

    @property
    def key(self) -> str | None:
        """
        Returns the lowercase recorder type. If the type contains the suffix
        "Recorder", this is removed to ensure consistency (a recorder can be
        initialised with or without the suffix in the JSON file).
        :return: The key of the recorder.
        """
        return self.string_to_key(self.type)

    @property
    def is_custom(self) -> bool:
        """
        Returns True if the recorder is custom.
        :return: True if the recorder is custom, False otherwise.
        """
        if self.key is None:
            return False

        if self.key in PywrRecordersData().keys:
            return False

        return True

    @property
    def is_a_model_recorder(self) -> bool:
        """
        Checks if the recorder name is defined in the "recorders" key of the model
        dictionary.
        :return: True if the recorder is a model recorder, False for anonymous
        recorders.
        """
        if self.model_recorder_names is None or self.name is None:
            return False

        # normalise the names
        global_recorder_names = [
            name.lower() for name in self.model_recorder_names
        ]
        return self.name.lower() in global_recorder_names

    @property
    def humanised_type(self) -> str:
        """
        Returns a user-friendly string identifying the recorder type.
        :return The recorder type. This is the pywr recorder name for
        custom recorders.
        """
        pywr_recorders = PywrRecordersData()
        if self.is_custom:
            return self.type
        else:
            return pywr_recorders.humanise_name(self.key)

    def humanise_attribute_name(self, attribute_name: str) -> str:
        """
        Renames a recoder attribute. The first letter is capitalised and some
        attributes are replaced with a more human-readable string (for example
        recorder_agg_func is converted to Aggregation function). Attributes of
        custom recorders are not renamed.
        :param attribute_name: The attribute name.
        :return: The renamed attribute name.
        """
        if self.is_custom:
            return attribute_name

        if "agg_func" in attribute_name:
            return "Aggregation function"
        elif attribute_name == "index_col":
            return "Column index"

        return attribute_name.title().replace("_", " ")

    @staticmethod
    def string_to_key(recorder_class: str | None) -> str | None:
        """
        Converts the recorder class or string in the dictionary "type" key to a
        recorder key (i.e. lower case string without the Recorder suffix).
        :param recorder_class: The recorder class or type.
        :return: The recorder key.
        """
        if not recorder_class:
            return None
        if recorder_class[-8:].lower() == "recorder":
            return recorder_class[0:-8].lower()
        else:
            return recorder_class.lower()

    def reset_props(self) -> None:
        """
        Empties the property dictionary.
        :return: None
        """
        self.props = {}
