from copy import deepcopy as dp

from pywr_editor.model import PywrParametersData

"""
 Handles a model parameter.
"""


class ParameterConfig:
    def __init__(
        self,
        props: dict,
        model_parameter_names: list[str] | None = None,
        name: str | None = None,
        deepcopy: bool = False,
    ):
        """
        Initialises the class.
        :param props: The parameter configuration.
        :param model_parameter_names: The list of parameter names in the "parameters"
        model section of the JSON dictionary.
        :param name: The parameter's name if available. Anonymous parameters (i.e.
        those nested in a node or a parameter) have no name.
        :param deepcopy: Whether to create a deepcopy of the dictionary
        """
        self.props = props
        if not isinstance(self.props, dict):
            self.props = {}

        self.model_parameter_names = model_parameter_names
        self.name = name
        if not isinstance(self.name, str):
            self.name = None

        if deepcopy:
            self.props = dp(self.props)

    @property
    def type(self) -> str | None:
        """
        Returns the parameter type.
        :return: The lowercase string identifying the parameter type.
        """
        if "type" in self.props and self.props["type"]:
            return self.props["type"]
        return None

    @property
    def key(self) -> str | None:
        """
        Returns the lowercase parameter type. If the type contains the suffix
        "Parameter", this is removed to ensure consistency (a parameter can be
        initialised with or without the suffix in the JSON file).
        :return: The key of the parameter.
        """
        return self.string_to_key(self.type)

    def delete_attribute(self, attribute: str | list) -> None:
        """
        Deletes an attribute or a list of attributes from the parameter's dictionary.
        :param attribute: The attribute or attributes to remove.
        :return: None
        """
        if isinstance(attribute, str):
            if attribute in self.props:
                del self.props[attribute]
        elif isinstance(attribute, list):
            for attr in attribute:
                if attr in self.props:
                    del self.props[attr]

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
        global_parameter_names = [
            name.lower() for name in self.model_parameter_names
        ]
        return self.name.lower() in global_parameter_names

    @property
    def is_custom(self) -> bool:
        """
        Returns True if the parameter is custom. A parameter is custom if its "type"
        is not a Pywr built-in parameter type.
        :return: True if the parameter is custom, False otherwise.
        """
        if self.key is None:
            return False

        if self.key in PywrParametersData().keys:
            return False

        return True

    def humanise_attribute_name(self, attribute_name: str) -> str:
        """
        Renames a parameter attribute. For example agg_func is converted to
        "Aggregation function". Attributes of custom parameters are not renamed.
        :param attribute_name: The attribute name.
        :return: The renamed attribute name.
        """
        # do not convert custom parameters' attributes
        if self.is_custom:
            return attribute_name

        if attribute_name == "agg_func":
            return "Aggregation function"
        elif attribute_name == "index_col":
            return "Column index"
        elif attribute_name == "params":
            return "Parameters"
        elif attribute_name == "h5file":
            return "URL"

        return attribute_name.title().replace("_", " ")

    @property
    def humanised_type(self) -> str:
        """
        Returns a user-friendly string identifying the parameter type.
        :return The parameter type. This is the pywr parameter name for
        custom parameters.
        """
        pywr_parameters = PywrParametersData()
        if self.is_custom:
            return self.type
        else:
            return pywr_parameters.humanise_name(self.key)

    def reset_props(self) -> None:
        """
        Empties the property dictionary.
        :return: None
        """
        self.props = {}

    @staticmethod
    def string_to_key(param_class: str | None) -> str | None:
        """
        Converts the parameter class or type (the string in the dictionary "type" key)
        to a parameter key (i.e. lower case string without the Parameter suffix).
        :param param_class: The parameter class or type.
        :return: The parameter key.
        """
        if not param_class:
            return None
        if param_class[-9:].lower() == "parameter":
            return param_class[0:-9].lower()
        else:
            return param_class.lower()
