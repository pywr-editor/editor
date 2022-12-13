import pytest
from pywr_editor.model import ModelConfig, ScenarioConfig
from test.utils import resolve_model_path


class TestScenarios:
    @staticmethod
    @pytest.fixture
    def model(file):
        if file is not None:
            return ModelConfig(resolve_model_path(file))
        else:
            return ModelConfig()

    @pytest.mark.parametrize(
        "file, expected",
        [("model_1.json", ["scenario A", "scenario B"]), ("model_2.json", [])],
    )
    def test_names(self, file, model, expected):
        """
        Tests that the names are retrieved correctly.
        """
        assert model.scenarios.names == expected
        assert model.scenarios.count == len(expected)

    @pytest.mark.parametrize("file", ["model_1.json"])
    def test_find_scenario_index_by_name(self, file, model):
        """
        Tests the find_scenario_index_by_name method.
        """
        scenarios = model.scenarios
        assert scenarios.find_scenario_index_by_name("scenario A") == 0
        assert scenarios.find_scenario_index_by_name("scenario B") == 1
        assert scenarios.find_scenario_index_by_name("Non existing") is None

    @pytest.mark.parametrize("file", ["model_1.json"])
    def test_get_config_from_name(self, file, model):
        """
        Tests the get_config_from_name method.
        """
        scenarios = model.scenarios

        scenario_a = {
            "name": "scenario A",
            "size": 10,
        }
        assert scenarios.get_config_from_name("scenario A") == scenario_a
        assert isinstance(
            scenarios.get_config_from_name("scenario A", as_dict=False),
            ScenarioConfig,
        )

        assert scenarios.get_config_from_name("scenario B") == {
            "name": "scenario B",
            "size": 2,
            "ensemble_names": ["First", "Second"],
        }

    @pytest.mark.parametrize("file", ["model_1.json"])
    def test_get_size_from_name(self, file, model):
        """
        Tests the get_size_from_name method.
        """
        scenarios = model.scenarios
        sizes = {
            "scenario A": 10,
            "scenario B": 2,
            "Non-existing": None,
            None: None,
        }
        for name, expected_size in sizes.items():
            assert scenarios.get_size_from_name(name) == expected_size

    @pytest.mark.parametrize("file", ["model_1.json"])
    def test_update(self, file, model):
        """
        Tests the update method.
        """
        scenarios = model.scenarios

        # replace existing scenario
        new_dict = {
            "name": "scenario C",
            "size": 123,
            "ensemble_names": ["First", "Second"],
        }
        scenarios.update("scenario B", new_dict)
        assert model.has_changes is True
        assert scenarios.get_config_from_name("scenario B") is None
        assert scenarios.get_config_from_name("scenario C") == new_dict

        # add a new scenario
        new_dict = {
            "name": "scenario X",
            "size": 6,
        }
        scenarios.update("scenario X", new_dict)
        assert model.has_changes is True
        assert scenarios.get_config_from_name("scenario X") == new_dict
        assert scenarios.count == 3

    @pytest.mark.parametrize(
        "file, scenario_name, expected",
        [
            ("model_1.json", "scenario A", 1),
            ("model_1.json", "scenario B", 0),
            ("model_2.json", "scenario A", 0),
        ],
    )
    def test_is_used(self, file, model, scenario_name, expected):
        """
        Tests that the names are retrieved correctly.
        """
        assert model.scenarios.is_used(scenario_name) == expected

    @pytest.mark.parametrize(
        "file, scenario_name",
        [
            ("model_1.json", "scenario A"),
            ("model_1.json", "scenario B"),
            ("model_2.json", "scenario A"),
        ],
    )
    def test_delete(self, file, model, scenario_name):
        """
        Tests the delete method.
        """
        model.scenarios.delete(scenario_name)
        assert (
            model.scenarios.find_scenario_index_by_name(scenario_name) is None
        )

    @pytest.mark.parametrize(
        "file, scenario_name",
        [
            ("model_1.json", "scenario A"),
            ("model_1.json", "scenario B"),
        ],
    )
    def test_rename(self, file, model, scenario_name):
        """
        Tests the rename method.
        """
        new_name = "New name"
        model.scenarios.rename(scenario_name, new_name)

        assert model.scenarios.does_scenario_exist(scenario_name) is False
        assert model.scenarios.does_scenario_exist(new_name) is True

        if scenario_name == "scenario A":
            assert (
                model.parameters.get_config_from_name("param3", as_dict=True)[
                    "scenario"
                ]
                == new_name
            )


class TestScenarioConfig:
    @pytest.mark.parametrize(
        "scenario_dict",
        [
            {
                "name": "scenario A",
                "size": 10,
            },
            {
                "name": "scenario B",
                "size": 2,
                "ensemble_names": ["First", "Second"],
            },
            # missing size
            {
                "name": "scenario C",
            },
            # missing name
            {
                "size": 20,
            },
        ],
    )
    def test_props(self, qtbot, scenario_dict):
        """
        Tests the class properties
        """
        config = ScenarioConfig(props=scenario_dict)
        props = ["name", "size", "ensemble_names"]
        for prop in props:
            if prop in scenario_dict:
                assert getattr(config, prop) == scenario_dict[prop]
            elif prop == "size":
                assert getattr(config, prop) == 1
            elif prop == "ensemble_names":
                assert getattr(config, prop) == []
            else:
                assert getattr(config, prop) is None
