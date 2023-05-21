import ast
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeVar

import pywr_editor.model as model
from pywr_editor.model import (
    PywrNodesData,
    PywrParametersData,
    PywrRecordersData,
)

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig

"""
 Class containing the import information
"""


@dataclass
class ImportProps:
    name: str | None = None
    """ The Python file name """
    parameters: list[str] | None = None
    """ The parameter class names in the file """
    recorders: list[str] | None = None
    """ The recorder class names in the file """
    nodes: list[str] | None = None
    """ The node class names in the file """
    exists: list[str] | None = None
    """ Whether the file exists """
    base_classes: dict[str, list[str]] | None = None
    """ The base classes for each class in the file """

    def __post_init__(self):
        self.parameters = self.parameters if self.parameters else []
        self.recorders = self.recorders if self.recorders else []
        self.nodes = self.nodes if self.nodes else []
        self.exists = self.exists if self.exists is not None else False


"""
 Class used to handle the "includes" key in the model
 dictionary. Only Python files are supported
"""

comp_dict_info_type = TypeVar(
    "comp_dict_info_type", bound=dict[str, dict[str, list | str]]
)


@dataclass
class Includes:
    model: "ModelConfig"
    """ The ModelConfig instance """

    def __post_init__(self):
        # custom classes can inherit from a base class or an existing Pywr component
        self.parameter_base_classes = PywrParametersData().classes + [
            "Parameter",
            "IndexParameter",
        ]
        self.recorder_base_classes = PywrRecordersData().classes + [
            "Recorder",
        ]
        self.node_base_classes = PywrNodesData().classes + [
            "Node",
        ]

    def get_all_non_pyfiles(self) -> list[str]:
        """
        Returns the list of non Python files.
        :return: The list of non Pyton files as they are included in the JSON file.
        """
        return [
            file for file in self.model.json["includes"] if not file.endswith(".py")
        ]

    def get_all_files(self, include_non_existing: bool) -> list[Path]:
        """
        Returns the list of Python files.
        :param include_non_existing: When False, exclude non-existing files from the
        list.
        :return: The list of Pyton files with absolute paths.
        """
        if "includes" in self.model.json:
            all_files = []
            for file in self.model.json["includes"]:
                # include Python files only
                if not file.endswith(".py"):
                    continue
                # exclude missing files
                if not include_non_existing and not self.model.does_file_exist(file):
                    continue

                all_files.append(Path(self.model.normalize_file_path(file)))
            return all_files
        return []

    def get_classes_from_file(self, file: str | Path) -> ImportProps:
        """
        Returns a list of classes for custom nodes, parameters and recorders in the
        file.
        :param file: The path to the file.
        :return: A dictionary with the classes for nodes, parameters and recorders.
        """
        file = Path(file)
        class_names = ImportProps(name=file.name)

        if file.exists() is False:
            return class_names

        with open(file) as fid:
            class_names.exists = True
            class_names.base_classes = {}

            node = ast.parse(fid.read())
            # get the class name and its base classes
            for n in node.body:
                if isinstance(n, ast.ClassDef):
                    # check that the class inherits from one of the pywr classes
                    # noinspection PyUnresolvedReferences
                    file_base_classes = {base_class.id for base_class in n.bases}
                    base_class_list = sorted(list(file_base_classes))

                    # class is a Parameter
                    if (
                        len(
                            set.intersection(
                                file_base_classes,
                                set(self.parameter_base_classes),
                            )
                        )
                        > 0
                    ):
                        class_names.parameters.append(n.name)
                        class_names.base_classes[n.name] = base_class_list
                    # class is a Recorder
                    elif (
                        len(
                            set.intersection(
                                file_base_classes,
                                set(self.recorder_base_classes),
                            )
                        )
                        > 0
                    ):
                        class_names.recorders.append(n.name)
                        class_names.base_classes[n.name] = base_class_list
                    # class is a Node
                    elif (
                        len(
                            set.intersection(
                                file_base_classes, set(self.node_base_classes)
                            )
                        )
                        > 0
                    ):
                        class_names.nodes.append(n.name)
                        class_names.base_classes[n.name] = base_class_list

        return class_names

    def get_custom_classes(
        self, include_non_existing: bool = False
    ) -> dict[Path, ImportProps]:
        """
        Returns a list of custom classes names of nodes, parameters and recorders in
        each included file.
        :param include_non_existing: Exclude non-existing file from the list.
        Default to False.
        :return: The list of class names.
        """
        return {
            file: self.get_classes_from_file(file)
            for file in self.get_all_files(include_non_existing)
        }

    def get_custom_components(
        self, comp_type: Literal["parameter", "node", "recorder"]
    ) -> comp_dict_info_type:
        """
        Returns a list of dictionary with custom component class information from all
        import files.
        :param comp_type: The type of component ("parameter", "node" or "recorder").
        :return: Returns a dictionary with the custom component key as key and
        a dictionary with the components' information as values.
        """
        config_methods = {
            "parameter": "ParameterConfig",
            "node": "NodeConfig",
            "recorder": "RecorderConfig",
        }
        if comp_type not in config_methods:
            raise ValueError(
                "The comp_type argument can only be 'parameter', 'node' or 'recorder'"
            )

        custom_components = {}
        for data_dict in self.get_custom_classes().values():
            for class_name in getattr(data_dict, f"{comp_type}s"):
                key = getattr(model, config_methods[comp_type])().string_to_key(
                    class_name
                )
                custom_components[key] = {
                    "name": class_name,
                    "class": class_name,
                    "sub_classes": data_dict.base_classes[class_name],
                }
        return custom_components

    def get_custom_parameters(self) -> comp_dict_info_type:
        """
        Returns a list of dictionary with custom parameter class information from all
        import files.
        :return: Returns a dictionary with the custom parameter key as key and
        a dictionary with the parameters' information as values.
        """
        return self.get_custom_components("parameter")

    def get_custom_recorders(self) -> comp_dict_info_type:
        """
        Returns a list of dictionary with custom recorder class information from all
        import files.
        :return: Returns a dictionary with the custom recorder key as key and
        a dictionary with the recorders' information as values.
        """
        return self.get_custom_components("recorder")

    def get_custom_nodes(self) -> comp_dict_info_type:
        """
        Returns a list of dictionary with custom node class information from all
        import files.
        :return: Returns a dictionary with the custom node key as key and
        a dictionary with the nodes' information as values.
        """
        return self.get_custom_components("node")

    def get_keys_with_subclass(
        self,
        subclass_name: str,
        comp_type: Literal["parameter", "node", "recorder"],
    ) -> list[str]:
        """
        Returns the keys of custom imported components, when subclass_name is
        in the subclasses.
        :param subclass_name: The name of the subclass, for example IndexParameter.
        :param comp_type: The type of component ("parameter", "node" or "recorder").
        :return: A list of custom component keys.
        """
        methods = {
            "parameter": "get_custom_parameters",
            "node": "get_custom_nodes",
            "recorder": "get_custom_recorders",
        }
        if comp_type not in methods:
            raise ValueError(
                "The comp_type argument can only be 'parameter', 'node' or 'recorder'"
            )

        keys = []
        for key, data in getattr(self, methods[comp_type])().items():
            if subclass_name in data["sub_classes"]:
                keys.append(key)

        return keys

    def save(self, files: list[str]) -> None:
        """
        Saves the list of imports.
        :param files: The file list.
        :return: None
        """
        self.model.json["includes"] = files
        self.model.has_changed()
