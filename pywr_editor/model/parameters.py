from typing import TYPE_CHECKING

from pywr_editor.model import ComponentsDict, ParameterConfig

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig

"""
 Handles the model parameters.
"""


class Parameters(ComponentsDict):
    def __init__(self, model: "ModelConfig"):
        """
        Initialise the class
        :param model: The ModelConfig instance.
        """
        super().__init__(model, "parameters")

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
        return parameter_name in self.get_all().keys()

    def config(
        self, parameter_name: str, as_dict: bool = True
    ) -> dict | ParameterConfig | None:
        """
        Return the configuration of a model parameter as dictionary or ParameterConfig
        instance.
        :parameter parameter_name: The component name.
        :param as_dict: Return the configuration as dictionary when true, the
        ParameterConfig instance when false.
        :return: The component configuration or its instance.
        """
        if self.exists(parameter_name) is False:
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
