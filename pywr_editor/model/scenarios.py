from dataclasses import dataclass
from typing import TYPE_CHECKING

from pywr_editor.model import JsonUtils, ScenarioConfig

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig


@dataclass
class Scenarios:
    model: "ModelConfig"
    """ The ModelConfig instance """

    def get_all(self) -> list[dict]:
        """
        Return the list of scenario dictionaries.
        :return: The list of dictionaries with the scenario configurations or an empty
        list if the scenarios are not configured.
        """
        return self.model.json["scenarios"]

    @property
    def names(self) -> list[dict]:
        """
        Return the list of scenario names.
        :return: The scenario names.
        """
        if "scenarios" not in self.model.json:
            return []
        return [
            scenario_dict["name"]
            for scenario_dict in self.model.json["scenarios"]
            if "name" in scenario_dict
        ]

    @property
    def count(self) -> int:
        """
        Return the total number of scenarios.
        :return: The edges count.
        """
        return len(self.get_all())

    def find_index(self, scenario_name: str) -> int | None:
        """
        Find the scenario index in the list by the scenario name.
        :param scenario_name: The scenario to look for.
        :return: The scenario index if the name is found. None otherwise.
        """
        return next(
            (
                idx
                for idx, scenario in enumerate(self.get_all())
                if scenario["name"] == scenario_name
            ),
            None,
        )

    def exists(self, scenario_name: str) -> bool:
        """
        Check if a scenario name exists.
        :param scenario_name: The scenario name to check.
        :return: True if the scenario exists, False otherwise.
        """
        return self.find_index(scenario_name) is not None

    def config(
        self, scenario_name: str, as_dict: bool = True
    ) -> ScenarioConfig | dict | None:
        """
        Find the scenario configuration dictionary by its name.
        :param scenario_name: The scenario to look for.
        :param as_dict: Returns the configuration as dictionary when True, the
        ScenarioConfig instance if False.
        :return: The scenario configuration if found, None otherwise.
        """
        scenario_idx = self.find_index(scenario_name)
        if scenario_idx is not None:
            scenario_dict = self.get_all()[scenario_idx]
            if as_dict:
                return scenario_dict
            else:
                return ScenarioConfig(props=scenario_dict)
        return None

    def get_size(self, scenario_name: str) -> int | None:
        """
        Find the scenario size by its name.
        :param scenario_name: The scenario to look for.
        :return: The scenario size if found, None otherwise.
        """
        if scenario_name is None or not self.exists(scenario_name):
            return None

        return self.config(scenario_name, as_dict=False).size

    def update(self, scenario_name: str, scenario_dict: dict) -> None:
        """
        Replace the scenario dictionary for an existing scenario or create a new one
        if it does not exist.
        :param scenario_name: The scenario name to add or update.
        :param scenario_dict: The scenario dictionary with the fields to add or update.
        :return: None
        """
        scenario_idx = self.find_index(scenario_name)

        # add name if it is missing
        if "name" not in scenario_dict:
            scenario_dict["name"] = scenario_name

        # add a new scenario
        if scenario_idx is None:
            self.model.json["scenarios"].append(scenario_dict)
            self.model.has_changed()
        else:
            self.model.json["scenarios"][scenario_idx] = scenario_dict
            self.model.has_changed()

    def is_used(self, scenario_name: str) -> int:
        """
        Check if the given scenario name is being used in the model.
        :param scenario_name: The name of the scenario.
        :return: The number of model components using the scenario. If the scenario
        does not exist, this returns 0.
        """
        if self.exists(scenario_name) is False:
            return 0

        # parameters uses "scenario" as key to specify a scenario name
        dict_utils = JsonUtils(self.model.json).find_str(
            string=scenario_name, match_key="scenario"
        )
        return dict_utils.occurrences

    def delete(self, scenario_name: str) -> None:
        """
        Delete a scenario from the model.
        :param scenario_name: The name of the scenario to delete.
        :return: None
        """
        scenario_idx = self.find_index(scenario_name)
        if scenario_idx is None:
            return None

        try:
            del self.model.json["scenarios"][scenario_idx]
            self.model.has_changed()
        except KeyError:
            pass

    def rename(self, scenario_name: str, new_name: str) -> None:
        """
        Rename a scenario. This changes the model dictionary values matching the
        current name with the name and whose key is "scenario".
        :param scenario_name: The scenario to rename.
        :param new_name: The new name.
        :return: None
        """
        scenario_idx = self.find_index(scenario_name)
        if scenario_idx is None:
            return None

        self.model.json["scenarios"][scenario_idx]["name"] = new_name

        # replace name in dictionary where key is "scenario"
        dict_utils = JsonUtils(self.model.json)
        self.model.json = dict_utils.replace_str(
            old=scenario_name, new=new_name, match_key="scenario"
        )
        self.model.has_changed()
