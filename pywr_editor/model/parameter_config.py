from copy import deepcopy as dp

from pywr_editor.model import ComponentConfig, PywrParametersData

"""
 Handles a model parameter.
"""


class ParameterConfig(ComponentConfig):
    def __init__(
        self,
        props: dict = None,
        model_parameter_names: list[str] | None = None,
        name: str | None = None,
        deepcopy: bool = False,
    ):
        """
        Initialise the class.
        :param props: The parameter configuration.
        :param model_parameter_names: The list of parameter names in the "parameters"
        model section of the JSON dictionary.
        :param name: The parameter's name if available. Anonymous parameters (i.e.
        those nested in a node or a parameter) have no name.
        :param deepcopy: Whether to create a deepcopy of the dictionary
        """
        super().__init__("parameter", props)

        self.name = name
        self.model_parameter_names = model_parameter_names
        if deepcopy:
            self.props = dp(self.props)

    @property
    def is_a_model_parameter(self) -> bool:
        """
        Checks if the parameter name is defined in the "parameters" key of the model
        dictionary.
        :return: True if the parameter is a model parameter, False for anonymous
        parameters.
        """
        if self.model_parameter_names is None or self.name is None:
            return False

        # normalise the names
        global_parameter_names = [name.lower() for name in self.model_parameter_names]
        return self.name.lower() in global_parameter_names

    @property
    def humanised_type(self) -> str:
        pywr_parameters = PywrParametersData()
        if self.is_custom:
            return self.type
        else:
            return pywr_parameters.humanise_name(self.key)

    @property
    def is_custom(self) -> bool:
        if self.key is None:
            return False

        if self.key in PywrParametersData().keys:
            return False

        return True
