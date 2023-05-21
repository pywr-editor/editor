import pytest

from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestNodesClass:
    @staticmethod
    def model(file: str | None) -> ModelConfig:
        """
        Loads the model.
        :param file: The file to load or None.
        :return: The ModelConfig instance.
        """
        if file:
            return ModelConfig(resolve_model_path(file))
        else:
            return ModelConfig()

    def test_set_position(self):
        """
        Tests the set_position method.
        """
        model = self.model("model_1.json")
        node_index = 1
        # by name
        model.nodes.set_position([9.0, 10.0], node_name="Link")
        assert model.json["nodes"][node_index]["position"]["editor_position"] == [
            9,
            10,
        ]

        # by index
        model.nodes.set_position([5, 77], node_index=node_index)
        assert model.json["nodes"][node_index]["position"]["editor_position"] == [
            5,
            77,
        ]

        assert model.has_changes is True

    def test_set_position_missing_props(self):
        """
        Tests the set_position method when the node does not have the position keys
        set.
        """
        model = self.model("model_missing_schematic_props.json")

        model.nodes.set_position([9, 10], node_name="Link1")
        assert model.json["nodes"][1]["position"]["editor_position"] == [9, 10]

        model.nodes.set_position([12, 78], node_name="Link2")
        assert model.json["nodes"][2]["position"]["editor_position"] == [12, 78]

        model.nodes.set_position([55, 410], node_name="Link3")
        assert model.json["nodes"][3]["position"]["editor_position"] == [
            55,
            410,
        ]

    def test_find_node_index(self):
        """
        Tests the find_node_index_by_name method.
        """
        model = self.model("model_missing_schematic_props.json")

        nodes = model.nodes
        assert nodes.find_node_index_by_name("Reservoir") == 0
        assert nodes.find_node_index_by_name("Link1") == 1
        assert nodes.find_node_index_by_name("Link3") == 3

    def test_delete_nodes(self):
        """
        Tests the delete method to delete a node and its edges.
        """
        model = self.model("model_delete_edges.json")
        nodes = model.nodes

        nodes.delete("Reservoir")
        assert model.nodes.find_node_index_by_name("Reservoir") is None
        assert model.edges.targets("Reservoir") is None

        nodes.delete("Link3")
        assert nodes.find_node_index_by_name("Link3") is None
        assert model.edges.targets("Link3") is None

    def test_delete_virtual_node(self):
        """
        Tests the removal of a virtual node (w/o any edge).
        """
        model = self.model("model_delete_edges.json")

        nodes = model.nodes
        all_edges = model.edges.get_all().copy()

        nodes.delete("Virtual storage")
        assert model.nodes.find_node_index_by_name("Virtual storage") is None
        assert all_edges == model.edges.get_all()

        assert model.has_changes is True

    def test_delete_node(self):
        """
        Tests the delete method when a node does not exist
        """
        model = self.model("model_delete_edges.json")

        all_nodes = model.nodes.get_all().copy()

        model.nodes.delete("Non-existing node")
        assert all_nodes == model.nodes.get_all()
        assert model.has_changes is False

    def test_model_with_orphans(self):
        """
        Tests the find_orphans method with a model with orphaned nodes.
        """
        model = self.model("model_with_orphans.json")
        assert model.nodes.orphans() == ["Link3", "Link4", "Custom node"]

    def test_model_wo_orphans(self):
        """
        Tests the find_orphans method with a model without orphaned nodes.
        """
        model = self.model("model_wo_orphans.json")
        assert model.nodes.orphans() is None

    def test_add_new_node(self):
        """
        Tests the add method properly adds new nodes to the model configuration.
        """
        model = self.model("model_1.json")

        new_node_config = {"name": "New node", "type": "link"}
        model.nodes.add(new_node_config)
        assert model.has_changes is True
        assert model.nodes.get_all()[-1] == new_node_config

        try:
            model.nodes.add({"name": "Node with missing type"})
        except KeyError:
            assert True
        else:
            assert False

        try:
            model.nodes.add({"type": "link"})
        except KeyError:
            assert True
        else:
            assert False

    @pytest.mark.parametrize(
        "new_dict, expected_dict",
        [
            # node with position
            (
                {
                    "name": "Reservoir",
                    "type": "Storage",
                    "max_volume": 10,
                    "initial_volume": 0,
                },
                {
                    "name": "Reservoir",
                    "type": "Storage",
                    "max_volume": 10,
                    "initial_volume": 0,
                    "position": {"editor_position": [200, 500]},
                },
            ),
            # add edge_color
            (
                {
                    "name": "Reservoir",
                    "type": "Storage",
                    "max_volume": 35,
                    "initial_volume": 35,
                    "edge_color": "blue",
                    "node_style": "wtw",
                },
                {
                    "name": "Reservoir",
                    "type": "Storage",
                    "max_volume": 35,
                    "initial_volume": 35,
                    "position": {
                        "editor_position": [200, 500],
                        "edge_color": "blue",
                        "node_style": "wtw",
                    },
                },
            ),
        ],
    )
    def test_update_node_dict(self, new_dict, expected_dict):
        """
        Tests the update method to update the node configuration.
        """
        model = self.model("model_1.json")
        model.nodes.update(new_dict)
        assert model.has_changes is True
        assert model.nodes.config(new_dict["name"]) == expected_dict

    def test_rename(self):
        """
        Tests the rename method.
        """
        model = self.model("model_1.json")

        # rename existing node
        new_name = "New name"
        model.nodes.rename("Reservoir", new_name)
        assert model.nodes.find_node_index_by_name("Reservoir") is None
        assert model.nodes.find_node_index_by_name(new_name) is not None
        assert model.has_changes is True

        # check edges
        assert model.edges.get_all() == [[new_name, "Link"]]

        # check recorders
        assert model.recorders.config("storage_flow")["node"] == new_name
        assert model.recorders.config("storage")["node"] == new_name

        # non-existing node
        model.nodes.rename("LinkXX", "New name")
        assert model.nodes.find_node_index_by_name("LinkXX") is None
