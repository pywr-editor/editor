from ..node_dialog_form import NodeDialogForm
from .abstract_node_section import AbstractNodeSection


class OutputSection(AbstractNodeSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for an Output node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
