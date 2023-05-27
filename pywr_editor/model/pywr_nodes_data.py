from pywr_editor.model.pywr_data import PywrData

"""
 Utility class for pywr built-in nodes.
"""


class PywrNodesData(PywrData):
    def __init__(self):
        """
        Utility class to get the available pywr nodes and their information.
        """
        super().__init__("", ":model/node-data")
