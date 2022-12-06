from enum import Enum


class Constants(Enum):
    # key defying where to store the node's position
    POSITION_KEY = "editor_position"
    # key defying where to store the style describing the node's style
    NODE_STYLE_KEY = "node_style"
    # key defying where to store the style describing the edge colour
    EDGE_COLOR_KEY = "edge_color"
    # the name of the group for custom nodes
    CUSTOM_NODE_GROUP_NAME = "Custom"
    # default size of the schematic when this is not provided in the model file
    DEFAULT_SCHEMATIC_SIZE = [800, 600]
    # key where to store the schematic size
    SCHEMATIC_SIZE_KEY = "pywr_editor_schematic_size"
