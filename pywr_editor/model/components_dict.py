from dataclasses import dataclass
from typing import TYPE_CHECKING

from pywr_editor.model import JsonUtils

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig
"""
 Abstract class to handle model components that are provided as list of
 dictionaries in the JSON file (i.e parameters and recorders.)
"""


@dataclass
class ComponentsDict:
    model: "ModelConfig"
    """ The ModelConfig instance. """
    key: str = "generic component"
    """ The dictionary key holding the model components (for example "parameters" for
    model parameters) """

    def __post_init__(self):
        """
        Constructor.
        """
        self.comp_label_ = self.key[:-1]
        """ A label describing the component """

        self.exclude_keys_ = [
            "table",
            "type",
            "name",
            "edges",
            "node",
            "nodes",
            "storage_node",
            "index_col",
            "index",
            "column",
            "parse_dates",
            "url",
            "agg_func",
        ]
        """ List of dictionary keys to exclude when renaming a component """

    def get_all(self) -> dict:
        """
        Return the list of model components.
        :return: The components as list of dictionaries.
        """
        return self.model.json[self.key]

    @property
    def count(self) -> int:
        """
        Return the total number of model components.
        :return: The component count.
        """
        return len(self.get_all())

    @property
    def names(self) -> list[str] | None:
        """
        Return the list of all component names.
        :return: The component names.
        """
        if self.get_all() is not None:
            return list(self.get_all().keys())
        return None

    def exists(self, component_name: str) -> bool:
        """
        Check if a component name exists.
        :param component_name: The component name to check.
        :return: True if the component exists, False otherwise.
        """
        return self.names is not None and component_name in self.names

    def is_used(self, component_name: str) -> int:
        """
        Check if the given component name is being used in the model.
        :param component_name: The name of the component.
        :return: The number of model components using this component. If the component
        does not exist, this returns 0.
        """
        if self.exists(component_name) is False:
            return 0

        dict_utils = JsonUtils(self.model.json).find_str(string=component_name)
        # remove the occurrence of the name in the "parameters" key
        return dict_utils.occurrences - 1

    def delete(self, component_name):
        """
        Delete a component from the model.
        :param component_name: The component name to delete.
        :return: None
        """
        if self.exists(component_name) is False:
            return None

        try:
            del self.model.json[self.key][component_name]
            self.model.has_changed()
        except KeyError:
            pass

    def update(self, component_name: str, component_dict: dict) -> None:
        """
        Replace the component dictionary for an existing component or create a new one,
        if the name does not exist.
        :param component_name: The component name to add or update.
        :param component_dict: The component dictionary with the fields to add or
        update.
        :return: None
        """
        self.model.json[self.key][component_name] = component_dict
        self.model.has_changed()

    def rename(self, component_name: str, new_name: str) -> None:
        """
        Rename a component. This changes the name in the dictionary keys and in each
        model component using this component as string.
        :param component_name: The component to rename.
        :param new_name: The new component name.
        :return: None
        """
        if self.exists(component_name) is False:
            return None

        # rename key in "parameters"
        self.model.json[self.key][new_name] = self.model.json[self.key].pop(
            component_name
        )

        # rename references in model components
        self.model.json = JsonUtils(self.model.json).replace_str(
            old=component_name, new=new_name, exclude_key=self.exclude_keys_
        )
        self.model.has_changed()

    def type_from_name(self, component_name: str) -> str | None:
        """
        Return the model component type from its name.
        :parameter component_name: The component name.
        :return: The component type, None if this is not available.
        """
        if (
            self.exists(component_name) is False
            or "type" not in self.get_all()[component_name]
        ):
            return None

        return self.get_all()[component_name]["type"]

    def orphans(self) -> list[str] | None:
        """
        Finds orphaned components.
        :return: A list of orphaned component names or None if there are none.
        """
        if self.get_all() is None:
            return None

        component_names = []
        for component_name in self.get_all().keys():
            if self.is_used(component_name) == 0:
                component_names.append(component_name)

        if len(component_names) > 0:
            return component_names
        return None
