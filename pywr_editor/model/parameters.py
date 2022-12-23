from dataclasses import dataclass
from typing import TYPE_CHECKING

from pywr_editor.model import JsonUtils, ParameterConfig

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig

"""
 Handles the model parameters.
"""


@dataclass
class Parameters:
    model: "ModelConfig"
    """ The ModelConfig instance """

    def get_all(self) -> dict:
        """
        Returns the list of model parameters.
        :return: The parameters as list of dictionaries.
        """
        return self.model.json["parameters"]

    @property
    def count(self) -> int:
        """
        Returns the total number of model parameters.
        :return: The parameters count.
        """
        return len(self.get_all())

    @property
    def names(self) -> list[str] | None:
        """
        Returns the list of all parameter names.
        :return: The parameter names.
        """
        if self.get_all() is not None:
            return list(self.get_all().keys())
        return None

    def does_parameter_exist(self, parameter_name: str) -> bool:
        """
        Checks if a parameter name exists.
        :param parameter_name: The parameter name to check.
        :return: True if the parameter exists, False otherwise.
        """
        if self.names is None or parameter_name not in self.names:
            return False
        return True

    def parameter(
        self, config: dict, name: str | None = None, deepcopy: bool = False
    ) -> ParameterConfig:
        """
        Returns the ParameterConfig instance.
        :param config: The parameter configuration.
        :param name: The parameter's name. This is optional for anonymous parameters
        (i.e. parameters that are nested in other parameters or nodes).
        :param deepcopy: Create a deepcopy of the parameter dictionary.
        :return: The ParameterConfig instance.
        """
        return ParameterConfig(
            props=config,
            name=name,
            model_parameter_names=self.names,
            deepcopy=deepcopy,
        )

    def is_a_model_parameter(self, parameter_name: str) -> bool:
        """
        Returns True if the parameter is defined in the model dictionary.
        :parameter parameter_name: The parameter name.
        :return: True if the parameter is a model parameter, False for
        anonymous parameters.
        """
        if self.get_all() is None:
            return False

        return parameter_name in self.get_all().keys()

    def get_config_from_name(
        self, parameter_name: str, as_dict: bool = True
    ) -> dict | ParameterConfig | None:
        """
        Returns the parameter configuration as dictionary or ParameterConfig instance.
        :parameter parameter_name: The parameter name.
        :param as_dict: Returns the configuration as dictionary, As ParameterConfig
        instance if False.
        :return: The parameter configuration or its instance.
        """
        if self.does_parameter_exist(parameter_name) is False:
            return None

        parameter_config = self.get_all()[parameter_name]
        if as_dict:
            return parameter_config
        else:
            return ParameterConfig(
                props=parameter_config,
                model_parameter_names=self.names,
                name=parameter_name,
            )

    def get_type_from_name(self, parameter_name: str) -> str | None:
        """
        Returns the model parameter type from its name.
        :parameter parameter_name: The parameter name.
        :return: The parameter type, None if this is not available.
        """
        parameter_config = self.get_config_from_name(parameter_name)
        if parameter_config is None:
            return None

        return parameter_config["type"]

    def find_orphans(self) -> list[str] | None:
        """
        Finds orphaned parameters.
        :return: A list of orphaned parameter names or None if there are none.
        """
        if self.get_all() is None:
            return None

        parameter_names = []
        for parameter_name in self.get_all().keys():
            if self.is_used(parameter_name) == 0:
                parameter_names.append(parameter_name)

        if len(parameter_names) > 0:
            return parameter_names
        return None

    def update(self, parameter_name: str, parameter_dict: dict) -> None:
        """
        Replaces the parameter dictionary for an existing parameter or create a new one
        if it does not exist.
        :param parameter_name: The parameter name to add or update.
        :param parameter_dict: The parameter dictionary with the fields to add or
        update.
        :return: None
        """
        self.model.json["parameters"][parameter_name] = parameter_dict
        self.model.changes_tracker.add(
            f"Updated parameter '{parameter_name}' with the following values: "
            + f"{parameter_dict}"
        )

    def is_used(self, parameter_name: str) -> int:
        """
        Checks if the given parameter name is being used in the model.
        :param parameter_name: The name of the parameter.
        :return: The number of model components using the parameter.
        If the parameter does not exist, this returns 0.
        """
        if self.does_parameter_exist(parameter_name) is False:
            return 0

        dict_utils = JsonUtils(self.model.json).find_str(string=parameter_name)
        # remove the occurrence of the name in the "parameters" key
        return dict_utils.occurrences - 1

    def delete(self, parameter_name):
        """
        Deletes a parameter from the model.
        :param parameter_name: The parameter name to delete.
        :return: None
        """
        if self.does_parameter_exist(parameter_name) is False:
            return None

        try:
            del self.model.json["parameters"][parameter_name]
            self.model.changes_tracker.add(
                f"Deleted parameter {parameter_name}"
            )
        except KeyError:
            pass

    def rename(self, parameter_name: str, new_name: str) -> None:
        """
        Renames a parameter. This changes the name in the "parameters" dictionary and
        in each model component, where the parameter is referred.
        WARNING: if the same name is used for a node or table, this will be replaced
        everywhere potentially breaking the model as it is not possible to tell them
        apart.
        :param parameter_name: The parameter to rename.
        :param new_name: The new parameter name.
        :return: None
        """
        if self.does_parameter_exist(parameter_name) is False:
            return None

        # rename key in "parameters"
        self.model.json["parameters"][new_name] = self.model.json[
            "parameters"
        ].pop(parameter_name)

        # rename references in model components
        self.model.json = JsonUtils(self.model.json).replace_str(
            old=parameter_name,
            new=new_name,
            exclude_key=[
                # exclude name to prevent node replacement
                "table",
                "type",
                "name",
                "index_col",
                "index",
                "column",
                "parse_dates",
                "url",
                "agg_func",
            ],
        )
        self.model.changes_tracker.add(
            f"Change parameter name from {parameter_name} to {new_name}"
        )
