from pathlib import Path

import pandas as pd
import pytest

from pywr_editor.model import Constants, ModelConfig
from tests.utils import resolve_model_path


class TestModelConfig:
    @staticmethod
    def model(file: str | None = None) -> ModelConfig:
        """
        Initialises the ModelConfig class.
        :param file: The model configuration file name.
        :return: The ModelConfig instance.
        """
        if file is not None:
            return ModelConfig(resolve_model_path(file))
        else:
            return ModelConfig()

    def test_invalid_json(self):
        """
        Checks that the correct error message is returned when the JSON file is invalid.
        """
        model = self.model("invalid_json.json")
        assert model.is_valid() is False
        assert "JSONDecodeError" in model.load_error

    def test_file_not_found(self):
        """
        Checks that the correct error message is returned when the JSON file does
        not exist.
        """
        model = self.model("file.json")
        assert model.is_valid() is False
        assert "does not exist" in model.load_error

    def test_empty_model(self):
        """
        Checks that the empty model dictionary is returned, when no JSON file
        is provided.
        """
        model = self.model()
        assert model.json["metadata"]["minimum_version"] == "1.19.0"
        assert model.json["metadata"]["title"] == "New model"
        assert "Model created on" in model.json["metadata"]["description"]

        assert model.json["includes"] == []
        assert model.json["nodes"] == []
        assert model.json["edges"] == []
        assert model.json["timestepper"] == {}
        assert model.json["scenarios"] == []

    def test_duplicated_custom_class_name(self):
        """
        Checks that the correct error message is returned when a Python file, containing
        a custom parameter or node or recorder, has the same name as a Pywr class.
        """
        model = self.model("invalid_model_duplicated_custom_class_name.json")
        assert model.is_valid() is False
        assert "as a Pywr built-in class: MonthlyProfileParameter" in model.load_error

    def test_update_schematic_size(self):
        """
        Test the update_schematic_size method.
        """
        model = self.model("model_1.json")
        new_size = [9999, 555]
        model.update_schematic_size(new_size)
        assert model.schematic_size == new_size
        assert model.has_changes is True

    def test_missing_schematic_size(self):
        """
        Tests that the schematic_size prop returns the default schematic size when this
        is not available in the JSON file.
        """
        model = self.model("model_2.json")
        assert (
            model.schematic_size == Constants.DEFAULT_SCHEMATIC_SIZE.value
            and model.editor_config[Constants.SCHEMATIC_SIZE_KEY.value]
            == Constants.DEFAULT_SCHEMATIC_SIZE.value
        )

    def test_schematic_size(self):
        """
        Tests that the schematic_size prop returns the correct values
        """
        model = self.model("model_1.json")
        assert model.schematic_size == [1900, 1450]

    def test_validation_missing_props(self):
        """
        Tests that the model JSOn is filled with the missing keys.
        """
        model = self.model("invalid_model_missing_nested_props.json")
        assert model.json["parameters"] == {}

    def test_validation_model_wrong_type(self):
        """
        Tests that the model fails validation (the nodes field is a dict instead of
        list)
        """
        model = self.model("invalid_model_wrong_type.json")
        assert model.is_valid() is False
        assert "The value for the 'nodes' key must be a list" in model.load_error

    def test_validation_missing_node_type(self):
        """
        Tests that the model fails validation (the node type field is missing)
        """
        model = self.model("invalid_model_missing_node_type.json")
        assert model.is_valid() is False
        assert (
            "The node at position 1 does not have a valid 'type' key"
            in model.load_error
        )

    def test_validation_missing_node_name(self):
        """
        Tests that the model fails validation (the node type field is missing)
        """
        model = self.model("invalid_model_missing_node_name.json")
        assert model.is_valid() is False
        assert (
            "The node at position 0 does not have a valid 'name' key"
            in model.load_error
        )

    def test_validation_duplicated_node_names(self):
        """
        Tests that the model fails validation (the node type field is missing)
        """
        model = self.model("invalid_model_duplicated_node_names.json")
        assert model.is_valid() is False
        assert (
            "The following node names are duplicated: Node 1, Node 4"
            in model.load_error
        )

    def test_validation_wrong_edges(self):
        """
        Tests that the model fails validation when an edge name is not a string
        """
        model = self.model("invalid_model_wrong_edges.json")
        assert model.is_valid() is False
        assert "The edge at position '0' must contain valid strings" in model.load_error

    def test_validation_missing_param_type(self):
        """
        Tests that the model fails validation (the parameter type field is missing)
        """
        model = self.model("model_parameters.json")
        assert model.is_valid() is False
        assert "The parameter 'param3' must have a valid 'type'" in model.load_error

    def test_timestepper_methods(self):
        """
        Tests the methods used to handle the timestepper information.
        """
        model = self.model("model_2.json")
        assert model.start_date == pd.to_datetime("2015-01-01")
        assert model.end_date == pd.to_datetime("2015-12-31")
        assert model.time_delta == 1
        assert model.number_of_steps == 365

    @pytest.mark.parametrize(
        "path, ignore_outside_model_path, expected",
        [
            # path is outside model folder and not converted to relative
            (
                Path(__file__).parent.parent.parent.parent / "a.csv",
                True,
                Path(__file__).parent.parent.parent.parent / "a.csv",
            ),
            # path is outside model folder but it is converted to relative
            (
                Path(__file__).parent.parent / "a.csv",
                False,
                "..\\a.csv",
            ),
            # relative paths are not changed
            (
                "../model/test.csv",
                False,
                "../model/test.csv",
            ),
            (
                "../model/test.csv",
                True,
                "../model/test.csv",
            ),
        ],
    )
    def test_path_to_relative(self, path, ignore_outside_model_path, expected):
        """
        Tests the path_to_relative method.
        """
        model = self.model("model_2.json")
        assert model.path_to_relative(path, ignore_outside_model_path) == str(expected)
