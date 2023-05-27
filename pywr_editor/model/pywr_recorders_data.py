from pywr_editor.model.pywr_data import PywrData

"""
 Utility class for pywr built-in recorders.
"""


class PywrRecordersData(PywrData):
    def __init__(self):
        """
        Load the resource with the recorders' data.
        """
        super().__init__("recorder", ":model/recorder-data")
