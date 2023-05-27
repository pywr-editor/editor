from pywr_editor.model.pywr_data import PywrData

"""
 Utility class for pywr built-in parameters.
"""


class PywrParametersData(PywrData):
    def __init__(self):
        """
        Load the resource with the parameters' data.
        """
        super().__init__("parameter", ":model/parameter-data")
