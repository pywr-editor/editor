from dataclasses import dataclass
from typing import TYPE_CHECKING

from pywr_editor.model import JsonUtils, RecorderConfig

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig

"""
 Handles the model recorders.

 Author: Stefano Simoncelli
"""


@dataclass
class Recorders:
    model: "ModelConfig"
    """ The ModelConfig instance """

    def get_all(self) -> dict[str, dict] | None:
        """
        Returns the recorders' dictionary if available.
        :return: The recorders' dictionary, None if it is not set.
        """
        return self.model.json["recorders"]

    @property
    def count(self) -> int:
        """
        Returns the total number of recorders.
        :return: The recorders count.
        """
        return len(self.get_all())

    def recorder(
        self, config: dict, name: str | None = None, deepcopy: bool = False
    ) -> RecorderConfig:
        """
        Returns the RecorderConfig instance.
        :param config: The recorder configuration.
        :param name: The recorder name.
        :param deepcopy: Create a deepcopy of the recorder dictionary.
        :return: The RecorderConfig instance
        """
        return RecorderConfig(
            props=config,
            name=name,
            model_recorder_names=self.names,
            deepcopy=deepcopy,
        )

    @property
    def names(self) -> list[str] | None:
        """
        Returns the list of all recorder names.
        :return: The recorder names.
        """
        if self.get_all() is not None:
            return list(self.get_all().keys())
        return None

    def does_recorder_exist(self, recorder_name: str) -> bool:
        """
        Checks if a recorder name exists.
        :param recorder_name: The recorder name to check.
        :return: True if the recorder exists, False otherwise.
        """
        if self.names is None or recorder_name not in self.names:
            return False
        return True

    def get_config_from_name(
        self, recorder_name: str, as_dict: bool = True
    ) -> dict | RecorderConfig | None:
        """
        Finds the recorder configuration dictionary by the recorder name.
        :param recorder_name: The recorder to look for.
        :param as_dict: Returns the configuration as dictionary. As RecorderConfig
        instance if False.
        :return: The recorder configuration if found, None otherwise.
        """
        if not self.does_recorder_exist(recorder_name):
            return None

        recorder_config = self.get_all()[recorder_name]
        if as_dict:
            return recorder_config
        else:
            return RecorderConfig(
                props=recorder_config,
                name=recorder_name,
                model_recorder_names=self.names,
            )

    def is_used(self, recorder_name: str) -> int:
        """
        Checks if the given recorder name is being used in the model.
        :param recorder_name: The name of the recorder.
        :return: The number of model components using the recorder.
        If the parameter does not exist, this returns 0.
        """
        if self.does_recorder_exist(recorder_name) is False:
            return 0

        dict_utils = JsonUtils(self.model.json).find_str(string=recorder_name)
        # remove the occurrence of the name in the "recorders" key
        return dict_utils.occurrences - 1

    def update(self, recorder_name: str, recorder_dict: dict) -> None:
        """
        Replaces the recorder dictionary for an existing recorder or create a new one
        if it does not exist.
        :param recorder_name: The recorder name to add or update.
        :param recorder_dict: The recorder dictionary with the fields to add or update.
        :return: None
        """
        self.model.json["recorders"][recorder_name] = recorder_dict
        self.model.changes_tracker.add(
            f"Updated recorder '{recorder_name}' with the following values: "
            + f"{recorder_dict}"
        )

    def rename(self, recorder_name: str, new_name: str) -> None:
        """
        Renames a recorder. This changes the name in the "recorders" dictionary and
        in each model component, where the recorder is referred.
        WARNING: if the same name is used for a node or table, this will be replaced
        everywhere potentially breaking the model as it is not possible to tell them
        apart.
        :param recorder_name: The recorder to rename.
        :param new_name: The new recorder name.
        :return: None
        """
        if self.does_recorder_exist(recorder_name) is False:
            return None

        # rename key in "recorders"
        self.model.json["recorders"][new_name] = self.model.json[
            "recorders"
        ].pop(recorder_name)

        # rename references in recorders key only - recorders are not used
        # by nodes or parameters
        self.model.json["recorders"] = JsonUtils(
            self.model.json["recorders"]
        ).replace_str(old=recorder_name, new=new_name)
        self.model.changes_tracker.add(
            f"Change recorder name from {recorder_name} to {new_name}"
        )

    def delete(self, recorder_name: str) -> None:
        """
        Deletes a recorder from the model.
        :param recorder_name: The recorder name to delete.
        :return: None
        """
        if self.does_recorder_exist(recorder_name) is False:
            return None

        try:
            del self.model.json["recorders"][recorder_name]
            self.model.changes_tracker.add(f"Deleted recorder {recorder_name}")
        except KeyError:
            pass
