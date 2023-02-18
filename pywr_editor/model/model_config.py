import json
import os
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from pandas import period_range

from pywr_editor.model import (
    ChangesTracker,
    Constants,
    Edges,
    Includes,
    ModelFileInfo,
    Nodes,
    Parameters,
    PywrNodesData,
    PywrParametersData,
    PywrRecordersData,
    Recorders,
    Scenarios,
    Tables,
)


@dataclass
class ModelConfig:
    json_file: str | None = None
    """The path to the model file"""

    def __post_init__(self) -> None:
        """
        Loads the model data.
        :return: None
        """
        # load the model
        self.json = dict()
        self.load_error = None
        self.load_model()
        # stop performing other tasks if the model cannot be loaded
        if not self.is_valid():
            return

        # add missing keys and validate the model
        self.check_missing_keys()
        self.validate()
        # stop performing other tasks if the model cannot be loaded
        if not self.is_valid():
            return

        # loads the module components
        self.changes_tracker = ChangesTracker()
        self.file = ModelFileInfo(self.json_file)
        self.nodes = Nodes(model=self)
        self.edges = Edges(model=self)
        self.parameters = Parameters(model=self)
        self.recorders = Recorders(model=self)
        self.tables = Tables(model=self)
        self.scenarios = Scenarios(model=self)
        self.includes = Includes(model=self)

        # pywr data
        self.pywr_parameter_data = PywrParametersData()
        self.pywr_recorder_data = PywrRecordersData()
        self.pywr_node_data = PywrNodesData()

        # custom components cannot use same name as built-in parameters. Pywr always
        # prioritises its own
        self.validate_custom_components()

    @property
    def metadata(self) -> dict | None:
        """
        Returns the metadata dictionary.
        :return: The metadata configuration
        """
        return self.json["metadata"]

    @property
    def title(self) -> str | None:
        """
        Returns the model title.
        :return: The model title.
        """
        return self.metadata["title"]

    @property
    def timestepper(self) -> dict | None:
        """
        Returns the timestepper dictionary.
        :return: The timestepper configuration
        """
        return self.json["timestepper"]

    @property
    def start_date(self) -> str | None:
        """
        Returns the timestepper start date.
        :return: The start date or None when not available.
        """
        if (
            "start" in self.timestepper
            and isinstance(self.timestepper["start"], str)
            and len(self.timestepper["start"].split("-")) == 3
        ):
            return self.timestepper["start"]
        return None

    @start_date.setter
    def start_date(self, date: str) -> None:
        """
        Updates the start date.
        :param date: The date as string.
        :return: None
        """
        self.changes_tracker.add(f"Changed start date to {date}")
        self.json["timestepper"]["start"] = date

    @property
    def end_date(self) -> str | None:
        """
        Returns the timestepper end date.
        :return: The end date as string or None when not available.
        """
        if (
            "end" in self.timestepper
            and isinstance(self.timestepper["end"], str)
            and len(self.timestepper["end"].split("-")) == 3
        ):
            return self.timestepper["end"]
        return None

    @end_date.setter
    def end_date(self, date: str) -> None:
        """
        Updates the end date.
        :param date: The date as string.
        :return: None
        """
        self.changes_tracker.add(f"Changed end date to {date}")
        self.json["timestepper"]["end"] = date

    @property
    def time_delta(self) -> int:
        """
        Returns the timestepper timestep.
        :return: The timestep or 1 when not available.
        """
        if "timestep" in self.timestepper and isinstance(
            self.timestepper["timestep"], int
        ):
            try:
                return int(self.timestepper["timestep"])
            except ValueError:
                return 1
        return 1

    @time_delta.setter
    def time_delta(self, time_delta: int) -> None:
        """
        Updates the timestepper timestep.
        :param time_delta: The new timestep as number of days.
        :return: The end date as datetime instance, None when not available.
        """
        self.changes_tracker.add(f"Changed timestep to {time_delta} days")
        self.json["timestepper"]["timestep"] = time_delta

    @property
    def number_of_steps(self) -> int | None:
        """
        Returns the number of time steps.
        :return: The time steps if the "timestepper" dictionary is properly configured.
        """
        range_vars = [self.start_date, self.end_date, self.time_delta]
        if all([v is not None for v in range_vars]):
            try:
                return len(
                    period_range(
                        self.start_date,
                        self.end_date,
                        freq=f"{self.time_delta}D",
                    )
                )
            except ValueError:
                return None
        return None

    @staticmethod
    def empty_model() -> dict:
        """
        Returns the configuration for an empty model.
        :return: The model configuration.
        """
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
        return {
            "metadata": {
                "minimum_version": 0.1,
                "title": "New model",
                "description": f"Model created on {current_time}",
            },
            "includes": [],
            "timestepper": {},
            "scenarios": [],
            "nodes": [],
            "edges": [],
            "tables": {},
        }

    def load_model(self) -> None:
        """
        Loads the model configuration as dictionary.
        :return: None.
        """
        self.json = self.empty_model()

        if not self.json_file:
            return

        # check file existence
        if os.path.exists(self.json_file) is False:
            self.load_error = f"The file '{self.json_file}' does not exist"
            return

        # check that the file is writable
        with open(self.json_file, "a") as fid:
            if not fid.writable():
                self.load_error = (
                    "You do not have write permissions to edit the model"
                )
                return

        try:
            with open(self.json_file, "r") as file:
                self.json = json.load(file)
        except Exception as e:
            self.load_error = (
                "The JSON file contains the following syntax error and "
                + f"cannot be loaded:\n\n{type(e).__name__}: {e}\n\n"
                + "Please fix the error by manually editing the JSON file"
            )

    def check_missing_keys(self) -> None:
        """
        Checks for missing keys in the dictionary.
        :return: None
        """
        # check for missing keys with array as value
        for key in ["nodes", "edges", "includes", "scenarios"]:
            if key not in self.json:
                self.json[key] = []

        # check for missing keys with dictionary as value
        for key in [
            "parameters",
            "recorders",
            "timestepper",
            "metadata",
            "tables",
        ]:
            if key not in self.json:
                self.json[key] = {}

        # check that the metadata dictionary and its key/value pairs are defined
        default_metadata = {
            "minimum_version": "0.1",
            "title": "Untitled",
            "description": "Missing description",
        }
        for key, value in default_metadata.items():
            if key not in self.json["metadata"] or not isinstance(
                self.json["metadata"][key], str
            ):
                self.json["metadata"][key] = value

    def is_valid(self) -> bool:
        """
        Checks if the model is valid.
        :return: True if the model is valid, False otherwise.
        """
        return self.load_error is None

    def validate(self) -> None:
        """
        Validates the model.
        :return: None
        """
        # additional explanation to append to the error messages below
        error_to_append = (
            "Please fix the error by manually editing the JSON file. This may "
            + "happen when you created or edited the model file outside of the editor"
        )

        # check the value type of the following keys
        value_types = {
            "metadata": dict,
            "parameters": dict,
            "timestepper": dict,
            "nodes": list,
            "edges": list,
            "includes": list,
            "scenarios": list,
        }
        for key, value_type in value_types.items():
            if not isinstance(self.json[key], value_type):
                self.load_error = (
                    f"The value for the '{key}' key must be a "
                    + f"{value_type.__name__}. {error_to_append}"
                )
                return

        # check that all nodes have the "name" and "type" keys and are strings
        for ni, node_config in enumerate(self.json["nodes"]):
            missing_key = None
            if "type" not in node_config or not isinstance(
                node_config["type"], str
            ):
                missing_key = "type"
            elif "name" not in node_config or not isinstance(
                node_config["name"], str
            ):
                missing_key = "name"
            if missing_key is not None:
                self.load_error = (
                    f"The node at position {ni} does not have a valid "
                    + f"'{missing_key}' key. {error_to_append}"
                )
                return

        # check the type, size of edges and that the node names exist
        all_node_names = [node["name"] for node in self.json["nodes"]]
        for ei, edge_config in enumerate(self.json["edges"]):
            # an edge must be a list of two elements at least (slots may be provided)
            if not isinstance(edge_config, list) or len(edge_config) < 2:
                self.load_error = (
                    f"The edge at position '{ei}' must be a list of at least two "
                    + f"items {error_to_append}"
                )
                return

            # node names must be strings
            if not all(
                [isinstance(edge_name, str) for edge_name in edge_config[0:2]]
            ):
                self.load_error = (
                    f"The edge at position '{ei}' must contain valid strings "
                    + f"{error_to_append}"
                )
                return

            # check that the edge nodes exist
            wrong_node_name = None
            if edge_config[0] not in all_node_names:
                wrong_node_name = edge_config[0]
            elif edge_config[1] not in all_node_names:
                wrong_node_name = edge_config[1]

            if wrong_node_name is not None:
                self.load_error = (
                    f"The node '{wrong_node_name}' for the edge at position "
                    + f"{ei} does not exist.  {error_to_append}"
                )
                return

        # check that node names are unique. pywr allows adding nodes with the same
        # name. However, when duplicated nodes  are connected to another node, the
        # last duplicated node is taken. Do not allow duplicated nodes as the name
        # uniquely identifies a node in pywr and the schematic.
        d = Counter(all_node_names)
        duplicated = [k for k, v in d.items() if v > 1]
        if len(duplicated) > 0:
            self.load_error = (
                "The following node names are duplicated: "
                + f"{', '.join(duplicated)}. Each node must have a unique name to "
                + f"be correctly identified. {error_to_append}"
            )
            return

        # check that all recorders and parameters have dictionaries and have the
        # "type" key
        for key in ["parameters", "recorders"]:
            if key in self.json.keys():
                for name, config in self.json["parameters"].items():
                    if not isinstance(config, dict) or len(config) == 0:
                        self.load_error = (
                            f"The {key[0:-1]} '{name}' must have a valid "
                            + f"dictionary as configuration. {error_to_append}"
                        )
                    elif "type" not in config.keys() or not isinstance(
                        config["type"], str
                    ):
                        self.load_error = (
                            f"The {key[0:-1]} '{name}' must have a valid 'type' "
                            + f"key. {error_to_append}"
                        )
                        return

    def validate_custom_components(self) -> None:
        """
        Validates custom parameters, recorders and nodes.
        :return: None
        """
        custom_param_dict = self.includes.get_custom_parameters()
        custom_parameter_keys = list(custom_param_dict.keys())
        if self.load_error is None and custom_param_dict:
            duplicated_keys = list(
                set(PywrParametersData().keys).intersection(
                    custom_parameter_keys
                )
            )
            if duplicated_keys:
                class_names = [
                    custom_param_dict[key]["class"] for key in duplicated_keys
                ]
                self.load_error = (
                    "The following custom parameter classes use the same "
                    + f"name as a Pywr built-in class: {', '.join(class_names)}. "
                    + "Remove or rename the classes to avoid any conflicts and "
                    + "undesired model behaviours"
                )

    @property
    def has_changes(self) -> bool:
        """
        Returns True if there are committed changes to the model configuration.
        :return: True if the model dictionary has changed. False otherwise.
        """
        return self.changes_tracker.changed

    def fetch_changes(self) -> list[dict]:
        """
        Returns the list of changes applied to the model.
        :return: A list of changes. Each element is a Change instance with the
        'timestamp' and 'message' as attributes.
        See ChangesTracker.
        """
        return self.changes_tracker.change_log

    def reload_file_info(self) -> None:
        """
        Updates the file information.
        :return: None
        """
        self.file = ModelFileInfo(self.json_file)

    def save(self) -> bool | str:
        """
        Saves the JSON file.
        :return: True if the file is successfully saved, the error message otherwise.
        """
        try:
            with open(self.json_file, "w") as outfile:
                json.dump(self.json, outfile, indent=2)
        except Exception as e:
            return f"The model cannot be saved because:\n\n{type(e).__name__}: {e}\n\n"

        self.reload_file_info()

        return True

    @property
    def schematic_size(self) -> list[float]:
        """
        Gets the size of the schematic.
        :return: The schematic size from the model config file. If not available or
        invalid, the default size is returned.
        """
        schematic_size_key = Constants.SCHEMATIC_SIZE_KEY.value
        default_schematic_size = Constants.DEFAULT_SCHEMATIC_SIZE.value
        if (
            schematic_size_key in self.json
            and isinstance(self.json[schematic_size_key], list)
            and len(self.json[schematic_size_key]) == 2
        ):
            return self.json[schematic_size_key]
        else:
            # store the schematic size if it is not set or wrong
            self.json[
                Constants.SCHEMATIC_SIZE_KEY.value
            ] = default_schematic_size
            return default_schematic_size

    def update_schematic_size(self, size: list[float]) -> None:
        """
        Sets the schematic size in the model config file.
        :param size: The width and height in pixel.
        :return: None
        """
        self.json[Constants.SCHEMATIC_SIZE_KEY.value] = size
        self.changes_tracker.add(f"Changed schematic size to {size}")

    def normalize_file_path(self, file: str | None) -> str | None:
        """
        If the path is relative, returns the absolute path from the model JSON file
        path. If the path is absolute, returns the same input.
        :param file: The file.
        :return: The file with the adjusted path.
        """
        if (
            file is not None
            and not os.path.isabs(file)
            and self.file.file_path is not None
        ):
            return os.path.normpath(os.path.join(self.file.file_path, file))
        return file

    def path_to_relative(
        self, path: str | Path, ignore_outside_model_path: bool = True
    ) -> str:
        """
        Converts the absolute path to a path relative to the model JSON file.
        :param path: The absolute path.
        :param ignore_outside_model_path: If the path is outside the model JSON
        path (i.e. it contains "..") the absolute path is returned. Default to True.
        :return: The relative path if the path is absolute and the JSON file has been
        saved.
        """
        if isinstance(path, Path):
            path = str(path)

        if path and os.path.isabs(path) and self.file.file_path:
            # on Windows relpath raise an exception if the two paths are on a
            # different drive
            try:
                rel_path = os.path.relpath(path, self.file.file_path)
                if not ignore_outside_model_path:
                    return rel_path
                elif ignore_outside_model_path and ".." not in rel_path:
                    return rel_path
                return path
            except ValueError:
                return path

        return path

    def does_file_exist(self, file: str) -> bool:
        """
        Checks if a file exists in the same folder of the model configuration. If the
        path is relative, the file is searched in the JSON file path.
        :param file: The file to search.
        :return: True if the file exists, False otherwise.
        """
        return os.path.exists(self.normalize_file_path(file))
