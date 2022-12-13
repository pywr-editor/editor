from pywr_editor.model import ModelConfig, Parameters
from tests.utils import resolve_model_path


class TestParameters:
    @staticmethod
    def parameters(file: str | None = None):
        """
        Initialises the Parameters class.
        :param file: The model file.
        :return: The Parameters instance.
        """
        if file is None:
            model = ModelConfig(resolve_model_path("model_3.json"))
        else:
            model = ModelConfig(resolve_model_path(file))
        return Parameters(model)

    def test_is_a_model_parameter(self):
        """
        Tests the is_a_model_parameter method.
        """
        parameters = self.parameters()
        assert parameters.is_a_model_parameter("param1") is True
        assert parameters.is_a_model_parameter("non_existing_param") is False

    def test_type_from_name(self):
        """
        Tests the get_type_from_name method.
        """
        parameters = self.parameters()
        assert parameters.get_type_from_name("param1") == "constant"
        assert parameters.get_type_from_name("non_existing_param") is None

    def test_count(self):
        """
        Tests the count property.
        """
        parameters = self.parameters()
        assert parameters.count == 3

    def test_get_config_from_name(self):
        """
        Tests the get_config_from_name method.
        """
        parameters = self.parameters()
        assert (
            parameters.get_config_from_name("param2", True)
            == parameters.model.json["parameters"]["param2"]
        )

    def test_model_with_orphans(self):
        """
        Tests the find_orphans method with a model with orphaned parameters.
        """
        parameters = self.parameters("model_with_orphans.json")
        assert parameters.find_orphans() == ["param2"]

    def test_model_without_orphans(self):
        """
        Tests the find_orphans method with a model without orphaned parameters.
        """
        parameters = self.parameters("model_wo_orphans.json")
        assert parameters.find_orphans() is None

    def test_update(self):
        """
        Tests the update method.
        """
        parameters = self.parameters("model_wo_orphans.json")
        model = parameters.model
        model.parameters.update("param1", {"type": "constant", "value": 3})
        assert model.has_changes is True
        assert model.parameters.get_config_from_name("param1") == {
            "type": "constant",
            "value": 3,
        }

        model.parameters.update("Parameter new", {})
        assert model.parameters.get_config_from_name("Parameter new") == {}

    def test_is_used(self):
        """
        Tests the is_used method.
        """
        parameters = self.parameters("model_with_orphans.json")
        model = parameters.model
        assert model.parameters.is_used("param1") == 3
        assert model.parameters.is_used("param3") == 1
        # orphan parameter
        assert model.parameters.is_used("param2") == 0
        # non-existing parameter
        assert model.parameters.is_used("Non-existing param") == 0

    def test_delete(self):
        """
        Tests the delete method.
        """
        parameters = self.parameters("model_with_orphans.json")
        model = parameters.model
        model.parameters.delete("param2")
        assert model.has_changes is True
        assert model.parameters.names == ["param1", "param3"]

    def test_rename(self):
        """
        Tests the rename method.
        """
        parameters = self.parameters("model_with_orphans.json")
        model = parameters.model

        model.parameters.rename("param1", "paramX")
        assert model.has_changes is True

        assert "param1" not in model.parameters.names
        assert "paramX" in model.parameters.names
        node_dict = model.nodes.get_node_config_from_name("Custom node")[
            "max_flow"
        ]
        assert node_dict["params"][0] == "paramX"
        assert node_dict["params"][2]["param_data"] == "paramX"

        assert (
            model.nodes.get_node_config_from_name("Link4")["max_flow"]
            == "paramX"
        )
