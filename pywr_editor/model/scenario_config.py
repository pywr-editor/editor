from copy import deepcopy as dp

"""
 Handle a scenario configuration
"""


class ScenarioConfig:
    def __init__(self, props: dict, deepcopy: bool = False):
        """
        Init the class.
        :param props: The scenario dictionary.
        :param deepcopy: Whether to create a deep copy of the dictionary.
        """
        self.props = props
        if deepcopy:
            self.props = dp(self.props)

    @property
    def size(self) -> int:
        """
        Returns the scenario size.
        :return: The size. If the "size" key is not available or less than 1, 1 is
        returned.
        """
        if "size" in self.props and self.props["size"] > 0:
            return self.props["size"]
        return 1

    @property
    def name(self) -> str | None:
        """
        Returns the scenario name.
        :return: The name, None if the "name" key is not available.
        """
        if "name" in self.props:
            return self.props["name"]
        return None

    @property
    def ensemble_names(self) -> list[str]:
        """
        Returns the ensemble names.
        :return: The names.
        """
        if "ensemble_names" in self.props:
            return self.props["ensemble_names"]
        return []
