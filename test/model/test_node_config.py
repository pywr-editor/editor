import json
import pytest
from pywr_editor.model import NodeConfig
from test.utils import resolve_model_path


@pytest.fixture
def node_config(node_props: dict) -> NodeConfig:
    """
    Returns the NodeConfig instance.
    :param node_props: The dictionary for the node,
    :return: The NodeConfig instance.
    """
    return NodeConfig(node_props)


def get_all_node_props() -> dict:
    """
    Reads the node properties file.
    :return: The dictionary with the node properties to test.
    """
    with open(resolve_model_path("node_config_props.json"), "r") as file:
        return json.load(file)


@pytest.mark.parametrize("node_props", [get_all_node_props()["node"]])
def test_custom_style(node_config, node_props):
    """
    Tests that the correct value is returned for the custom_style property.
    """
    assert node_config.custom_style == "wtw"


@pytest.mark.parametrize(
    "node_props", [get_all_node_props()["node_wo_position"]]
)
def test_node_wo_position(node_config, node_props):
    """
    Tests that the correct value is returned for the custom_style property.
    """
    assert node_config.custom_style is None


@pytest.mark.parametrize(
    "node_props", [get_all_node_props()["node_wo_node_style"]]
)
def test_node_wo_node_style(node_config, node_props):
    """
    Tests that the correct value is returned for the custom_style property.
    """
    assert node_config.custom_style is None


@pytest.mark.parametrize(
    "node_props", [get_all_node_props()["node_node_style_invalid_type"]]
)
def test_node_style_invalid_type(node_config, node_props):
    """
    Tests that the correct value is returned for the custom_style property.
    """
    assert node_config.custom_style is None


@pytest.mark.parametrize("node_props", [get_all_node_props()["node"]])
def test_position(node_config, node_props):
    """
    Tests that the correct value is returned for the position property.
    """
    assert node_config.position == [100, 200]


@pytest.mark.parametrize(
    "node_props", [get_all_node_props()["node_wrong_position"]]
)
def test_wrong_position(node_config, node_props):
    """
    Tests that the correct value is returned for the position property.
    """
    assert node_config.position is None
