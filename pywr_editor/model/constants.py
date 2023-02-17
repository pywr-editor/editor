from enum import Enum


class Constants(Enum):
    EDITOR_CONFIG_KEY = "pywr_editor"
    """ key in JSON containing the editor's settings """
    SHAPES_KEY = "shapes"
    """ key in editor's setting dictionary where to locate the shapes  """
    POSITION_KEY = "editor_position"
    """ key defying where to store the node's position """
    NODE_STYLE_KEY = "node_style"
    """ key defying where to store the style describing the node's style """
    EDGE_COLOR_KEY = "edge_color"
    """ key defying where to store the style describing the edge colour """
    CUSTOM_NODE_GROUP_NAME = "Custom"
    """ the name of the group for custom nodes"""
    DEFAULT_SCHEMATIC_SIZE = [800, 600]
    """ default size of the schematic when this is not provided in the model file """
    SCHEMATIC_SIZE_KEY = "schematic_size"
    """ key where to store the schematic size """
