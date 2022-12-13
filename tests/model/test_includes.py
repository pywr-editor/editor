import pytest
from pathlib import Path
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestIncludes:
    def test_get_all_files(self):
        """
        Tests the get_all_files method.
        """
        model = ModelConfig(resolve_model_path("model_1.json"))
        file_path = Path(__file__).parent.parent / "json_models" / "files"
        custom_param = file_path / "custom_parameter.py"
        custom_node = file_path / "custom_node.py"
        custom_recorder = file_path / "custom_recorder.py"
        custom_param2 = file_path / "custom_parameter2.py"
        assert model.includes.get_all_files(False) == [
            custom_param,
            custom_node,
            custom_recorder,
            custom_param2,
        ]
        assert model.includes.get_all_files(True) == [
            custom_param,
            custom_node,
            custom_recorder,
            custom_param2,
            file_path / "non_existing_file.py",
        ]

        assert model.includes.get_all_non_pyfiles() == ["model_2.json"]

        model = ModelConfig(resolve_model_path("model_2.json"))
        assert model.includes.get_all_files(False) == []

    @pytest.mark.parametrize(
        "file_name, class_attr, expected_classes",
        [
            (
                "custom_parameter.py",
                "parameters",
                [
                    "MyParameter",
                    "EnhancedMonthlyProfileParameter",
                    "LicenseParameter",
                ],
            ),
            (
                "custom_node.py",
                "nodes",
                ["LeakyPipe"],
            ),
            (
                "custom_recorder.py",
                "recorders",
                ["NodePlusRecorder"],
            ),
            ("non_existing.py", None, None),
        ],
    )
    def test_get_classes_from_file(
        self, file_name, class_attr, expected_classes
    ):
        """
        Tests the get_classes_from_file method.
        """
        model = ModelConfig(resolve_model_path("model_1.json"))
        # with non-existing file
        if file_name == "non_existing.py":
            classes = model.includes.get_classes_from_file(file_name)
            assert classes.parameters == []
            assert classes.recorders == []
            assert classes.nodes == []
        else:
            file_path = Path(__file__).parent.parent / "json_models" / "files"
            import_obj = model.includes.get_classes_from_file(
                str(file_path / file_name)
            )
            assert getattr(import_obj, class_attr) == expected_classes

    def test_get_custom_classes(self):
        """
        Tests the get_custom_classes method
        """
        model = ModelConfig(resolve_model_path("model_1.json"))

        found_names = []
        for import_obj in model.includes.get_custom_classes().values():
            found_names += (
                import_obj.parameters + import_obj.recorders + import_obj.nodes
            )
        assert found_names == [
            "MyParameter",
            "EnhancedMonthlyProfileParameter",
            "LicenseParameter",
            "LeakyPipe",
            "NodePlusRecorder",
            "My2Parameter",
        ]

    def test_custom_parameters(self):
        """
        Tests the get_custom_parameters method to handle custom parameters.
        """
        model = ModelConfig(resolve_model_path("model_1.json"))
        parameters = [
            "MyParameter",
            "EnhancedMonthlyProfileParameter",
            "LicenseParameter",
        ]

        # get all classes in imports
        file_path = Path(__file__).parent.parent / "json_models" / "files"
        classes = model.includes.get_custom_classes()

        # check first file
        file_name = "custom_parameter.py"
        file = file_path / file_name
        assert classes[file].name == file_name
        assert classes[file].parameters == parameters
        assert classes[file].recorders == []
        assert classes[file].nodes == []
        assert classes[file].base_classes == {
            "MyParameter": ["IndexParameter"],
            "EnhancedMonthlyProfileParameter": ["Parameter"],
            "LicenseParameter": [
                "MyClass",
                "Parameter",
            ],
        }

        # check second import
        file_name = "custom_parameter2.py"
        file = file_path / file_name
        assert classes[file].name == file_name
        assert classes[file].parameters == ["My2Parameter"]
        assert classes[file].recorders == []
        assert classes[file].nodes == []
        assert classes[file].base_classes == {
            "My2Parameter": ["DataFrameParameter"]
        }

        # check the parameters' information dictionary
        assert model.includes.get_custom_parameters() == {
            "my": {
                "class": "MyParameter",
                "name": "MyParameter",
                "sub_classes": ["IndexParameter"],
            },
            "enhancedmonthlyprofile": {
                "class": "EnhancedMonthlyProfileParameter",
                "name": "EnhancedMonthlyProfileParameter",
                "sub_classes": ["Parameter"],
            },
            "license": {
                "class": "LicenseParameter",
                "name": "LicenseParameter",
                "sub_classes": ["MyClass", "Parameter"],
            },
            "my2": {
                "class": "My2Parameter",
                "name": "My2Parameter",
                "sub_classes": ["DataFrameParameter"],
            },
        }

        # test get_keys_with_subclass
        assert model.includes.get_keys_with_subclass(
            "Parameter", "parameter"
        ) == [
            "enhancedmonthlyprofile",
            "license",
        ]

    def test_get_custom_recorders(self):
        """
        Tests the get_custom_recorders method to handle custom recorders.
        """
        model = ModelConfig(resolve_model_path("model_1.json"))
        recorders = ["NodePlusRecorder"]

        # get all classes in imports
        file_path = Path(__file__).parent.parent / "json_models" / "files"
        classes = model.includes.get_custom_classes()

        # check first file
        file_name = "custom_recorder.py"
        file = file_path / file_name
        assert classes[file].name == file_name
        assert classes[file].parameters == []
        assert classes[file].recorders == recorders
        assert classes[file].nodes == []
        assert classes[file].base_classes == {"NodePlusRecorder": ["Recorder"]}

        # check the recorders' information dictionary
        assert model.includes.get_custom_recorders() == {
            "nodeplus": {
                "class": "NodePlusRecorder",
                "name": "NodePlusRecorder",
                "sub_classes": ["Recorder"],
            }
        }

        # test get_keys_with_subclass
        assert model.includes.get_keys_with_subclass(
            "Recorder", "recorder"
        ) == ["nodeplus"]

    def test_get_custom_nodes(self):
        """
        Tests the get_custom_nodes method to handle custom recorders.
        """
        model = ModelConfig(resolve_model_path("model_1.json"))
        nodes = ["LeakyPipe"]

        # get all classes in imports
        file_path = Path(__file__).parent.parent / "json_models" / "files"
        classes = model.includes.get_custom_classes()

        # check first file
        file_name = "custom_node.py"
        file = file_path / file_name
        assert classes[file].name == file_name
        assert classes[file].parameters == []
        assert classes[file].recorders == []
        assert classes[file].nodes == nodes
        assert classes[file].base_classes == {"LeakyPipe": ["Node"]}

        # check the recorders' information dictionary
        assert model.includes.get_custom_nodes() == {
            "leakypipe": {
                "class": "LeakyPipe",
                "name": "LeakyPipe",
                "sub_classes": ["Node"],
            }
        }

        # test get_keys_with_subclass
        assert model.includes.get_keys_with_subclass("Node", "node") == [
            "leakypipe"
        ]
