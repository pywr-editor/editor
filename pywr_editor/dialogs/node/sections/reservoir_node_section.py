from ..node_dialog_form import NodeDialogForm
from .storage_section import StorageSection

"""
 Section to configure a Reservoir node. This is a Storage
 node but with a control curve on it. However the control
 curve option is not supported when the model is loaded via
 a JSON file. Only Parameter instances are supported.
"""


class ReservoirSection(StorageSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises a form section for a Reservoir node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
