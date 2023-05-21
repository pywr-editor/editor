from dataclasses import dataclass


@dataclass
class ComponentConfig:
    suffix: str = ""
    """ The component suffix (for example parameter for parameters) """
    props: dict = None
    """ The component configuration dictionary """

    def __post_init__(self):
        if not isinstance(self.props, dict):
            self.props = {}

    @property
    def type(self) -> str | None:
        """
        Returns the component type.
        :return: The lowercase string identifying the component type.
        """
        if "type" in self.props and self.props["type"]:
            return self.props["type"]
        return None

    @property
    def key(self) -> str | None:
        """
        Returns the lowercase component type. If the type contains the suffix
        (for example "Parameter"), this is removed to ensure consistency. A component
        can be initialised with or without the suffix in the JSON file.
        :return: The component key.
        """
        return self.string_to_key(self.type)

    def string_to_key(self, component_class: str | None) -> str | None:
        """
        Converts the component class or type (the string in the dictionary "type" key).
        :param component_class: The component class.
        :return: The component key.
        """
        if not component_class:
            return None
        if component_class[-9:].lower() == self.suffix:
            return component_class[0:-9].lower()
        else:
            return component_class.lower()

    def delete_attribute(self, attribute: str | list) -> None:
        """
        Delete an attribute or a list of attributes from the component's dictionary.
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
    def is_custom(self) -> bool:
        """
        Return True if the component is custom. A component is custom if its "type"
        is not a Pywr built-in parameter type.
        :return: True if the component is custom, False otherwise.
        """
        return False

    def humanise_attribute_name(self, attribute_name: str) -> str:
        """
        Rename a component attribute. For example agg_func is converted to
        "Aggregation function". Attributes of custom components are not renamed.
        :param attribute_name: The attribute name.
        :return: The renamed attribute name.
        """
        # do not convert custom component' attributes
        if self.is_custom:
            return attribute_name

        if attribute_name == "type":
            return attribute_name
        elif attribute_name == "agg_func":
            return "Aggregation function"
        elif attribute_name == "index_col":
            return "Column index"
        elif attribute_name == "params":
            return "Parameters"
        elif attribute_name == "h5file":
            return "URL"
        elif attribute_name == "mrf":
            return "Minimum residual flow"
        elif attribute_name == "mrf_cost":
            return "Minimum residual flow cost"
        elif attribute_name == "initial_volume_pc":
            return "Initial volume (%)"

        return attribute_name.title().replace("_", " ")

    @property
    def humanised_type(self) -> str:
        """
        Return a user-friendly string identifying the component type.
        :return The component type. This is the pywr component name for
        custom components.
        """
        raise NotImplementedError

    def reset(self) -> None:
        """
        Empty the component dictionary.
        :return: None
        """
        self.props = {}
