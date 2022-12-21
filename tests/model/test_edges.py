import pytest
from pywr_editor.model import Edges, ModelConfig
from tests.utils import resolve_model_path


class TestEdges:
    @staticmethod
    def edges(file: str) -> Edges:
        """
        Initialises the Edges class.
        :param file: The model configuration file name.
        :return: The Edges instance.
        """
        return Edges(ModelConfig(resolve_model_path(file)))

    def test_find_target_nodes(self):
        """
        Extracts target nodes.
        """
        edges = self.edges("model_2.json")
        assert edges.get_targets("Reservoir") == ["Link", "Link22"]

        edges = self.edges("model_3.json")

        # target exists
        assert edges.get_targets("Reservoir") == ["Link1"]
        # target Link222 does not exist
        assert edges.get_targets("Link1") is None
        # some target does not exist
        assert edges.get_targets("Link3") == ["Link4"]
        # provided source node does not exist
        assert edges.get_targets("ReservoirXXSSS") is None
        # source node does not exist
        assert edges.get_targets("Link35") is None

    def test_find_source_nodes(self):
        """
        Extracts source nodes.
        """
        edges = self.edges("model_delete_nodes.json")
        assert edges.get_sources("Link2") == ["Link1", "Link3"]
        assert edges.get_sources("Link1") == ["Reservoir"]

    @pytest.mark.parametrize(
        "slot_source, slot_target, expected_slots",
        [
            ("slot1", None, ["slot1"]),
            ("slot1", "slot2", ["slot1", "slot2"]),
            (None, "slot2", [None, "slot2"]),
            (None, None, []),
        ],
    )
    def test_add_edge(self, slot_source, slot_target, expected_slots):
        """
        Tests the add edge method.
        """
        edges = self.edges("model_4.json")
        edges.add("Node 1", "Node 2", slot_source, slot_target)
        edge, _ = edges.find_edge_by_index("Node 1", "Node 2")
        assert edge == ["Node 1", "Node 2"] + expected_slots

    def test_delete_edge1(self):
        """
        Tests that the edges are properly deleted.
        """
        edges = self.edges("model_4.json")

        # delete 1 edge
        edges.delete("Reservoir", "Link1")
        assert edges.get_targets("Reservoir") is None

        # non-existing node - no error thrown
        edges.delete("ReservoirXXX", "Link1")
        assert edges.model.has_changes is True

    def test_delete_edge2(self):
        """
        Tests that the edges are properly deleted.
        """
        edges = self.edges("model_delete_edges.json")

        # delete one edge
        edges.delete("Link3", "Link2")
        assert edges.get_targets("Link3") == ["Link4"]
        assert edges.model.has_changes is True

        # delete 2 edges
        edges.delete("Link3", "Link2")
        edges.delete("Link3", "Link4")
        assert edges.get_all() == [
            ["Reservoir", "Link1"],
            ["Link1", "Link2"],
            ["Reservoir", "Link2"],
        ]
        assert edges.model.has_changes is True

        # delete all edges
        edges.delete("Link3", "Link2")
        edges.delete("Link3", "Link4")
        edges.delete("Reservoir", "Link1")
        edges.delete("Reservoir", "Link2")
        edges.delete("Link1", "Link2")
        assert edges.get_all() == []
        assert edges.model.has_changes is True

    def test_delete_all_edge(self):
        """
        Tests that the edges are properly deleted.
        """
        edges = self.edges("model_delete_edges.json")

        # delete all edges for source node
        edges.delete(source_node_name="Reservoir")
        assert edges.get_targets("Reservoir") is None
        assert edges.model.has_changes is True

        assert edges.get_all() == [
            ["Link1", "Link2"],
            ["Link3", "Link2"],
            ["Link3", "Link4"],
        ]

    def test_find_edge_by_index(self):
        """
        Test the find_edge_by_index method.
        """
        edges = self.edges("model_2.json")
        assert edges.find_edge_by_index("Reservoir", "Link22") == (
            [
                "Reservoir",
                "Link22",
            ],
            1,
        )
        assert edges.find_edge_by_index("Reservoir", "Missing") == (None, None)

    @pytest.mark.parametrize(
        "source, target, slot_pos, expected_slot_name",
        [
            # edge with no slots
            ("Reservoir", "Link22", 1, None),
            ("Reservoir", "Link22", 2, None),
            # edge with slot for source node
            ("Node w slot", "Node 2", 1, 0),
            ("Node w slot", "Node 2", 2, None),
            # edge with slot for target node
            ("Node 3", "Node w slot", 1, None),
            ("Node 3", "Node w slot", 2, 1),
            # empty strings
            ("Node 1 w slot", "Node 2 w slot", 1, 0),
            ("Node 1 w slot", "Node 2 w slot", 2, 1),
        ],
    )
    def test_get_slot(self, source, target, slot_pos, expected_slot_name):
        """
        Tests the get_slot method.
        """
        edges = self.edges("model_2.json")
        assert (
            edges.get_slot(
                source_node_name=source,
                target_node_name=target,
                slot_pos=slot_pos,
            )
            == expected_slot_name
        )

    @pytest.mark.parametrize(
        "source, target, slot_pos, slot_name, expected_slots",
        [
            # edge with no slots
            ("Reservoir", "Link22", 1, "S", ["S"]),
            ("Reservoir", "Link22", 2, "S", [None, "S"]),
            ("Reservoir", "Link22", 1, 3, [3]),
            ("Reservoir", "Link22", 2, 7, [None, 7]),
            ("Reservoir", "Link22", 1, None, []),
            ("Reservoir", "Link22", 2, None, []),
            # edge with slot for source node
            ("Node w slot", "Node 2", 1, "A", ["A"]),
            ("Node w slot", "Node 2", 2, "C", [0, "C"]),
            ("Node w slot", "Node 2", 1, 3, [3]),
            ("Node w slot", "Node 2", 2, 8, [0, 8]),
            ("Node w slot", "Node 2", 1, None, []),
            ("Node w slot", "Node 2", 2, None, [0]),
            # edge with slot for target node
            ("Node 3", "Node w slot", 1, "A", ["A", 1]),
            ("Node 3", "Node w slot", 2, "C", [None, "C"]),
            ("Node 3", "Node w slot", 1, 7, [7, 1]),
            ("Node 3", "Node w slot", 2, 1, [None, 1]),
            ("Node 3", "Node w slot", 1, None, [None, 1]),
            ("Node 3", "Node w slot", 2, None, []),
            # edge with both slots
            ("Node 1 w slot", "Node 2 w slot", 1, "A", ["A", 1]),
            ("Node 1 w slot", "Node 2 w slot", 2, "C", [0, "C"]),
            ("Node 1 w slot", "Node 2 w slot", 1, 6, [6, 1]),
            ("Node 1 w slot", "Node 2 w slot", 2, 7, [0, 7]),
            ("Node 1 w slot", "Node 2 w slot", 1, None, [None, 1]),
            ("Node 1 w slot", "Node 2 w slot", 2, None, [0]),
            # empty strings
            ("Node 1 w slot", "Node 2 w slot", 1, " ", [None, 1]),
            ("Node 1 w slot", "Node 2 w slot", 1, "", [None, 1]),
        ],
    )
    def test_set_slot(
        self, source, target, slot_pos, slot_name, expected_slots
    ):
        """
        Tests the set_slot method.
        """
        edges = self.edges("model_2.json")
        edges.set_slot(
            source_node_name=source,
            target_node_name=target,
            slot_pos=slot_pos,
            slot_name=slot_name,
        )
        edge, _ = edges.find_edge_by_index(source, target)
        assert edge == [source, target] + expected_slots
