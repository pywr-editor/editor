from pywr_editor import MainWindow
from tests.utils import resolve_model_path


class TestDeleteSchematicNodes:
    model_file = resolve_model_path("model_dialog_parameters.json")

    def test_clone_node(self, qtbot) -> None:
        """
        Tests that a node can be cloned from the schematic.
        """
        window = MainWindow(self.model_file)
        window.hide()
        schematic = window.schematic
        node_name = "Link"
        model_config = schematic.model_config
        original_node_config = model_config.nodes.config(node_name, as_dict=False)

        node = schematic.node_items[node_name]
        node.on_clone_node()

        # 1. Check model configuration
        assert model_config.has_changes is True

        new_node_name = model_config.nodes.names[-1]
        new_node_config = model_config.nodes.config(new_node_name, as_dict=False)

        # the node dictionary is preserved
        node_dict = model_config.nodes.config(new_node_name)
        for prop in ["type", "min_flow", "max_flow"]:
            assert node_dict[prop] == original_node_config.props[prop]

        # position has changed
        assert original_node_config.position[0] + 100 == new_node_config.position[0]
        assert original_node_config.position[1] == new_node_config.position[1]

        # 2. Check schematic object
        assert new_node_name in schematic.node_items
