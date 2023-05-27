from copy import deepcopy as dp

from pywr_editor.model import ComponentConfig, PywrRecordersData

"""
 Handles a recorder.
"""


class RecorderConfig(ComponentConfig):
    def __init__(
        self,
        props: dict = None,
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
        super().__init__("recorder", props)
        self.name = name
        self.model_recorder_names = model_recorder_names

        if deepcopy:
            self.props = dp(self.props)

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
        global_recorder_names = [name.lower() for name in self.model_recorder_names]
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
