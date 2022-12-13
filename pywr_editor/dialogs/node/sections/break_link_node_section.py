from .abstract_node_section import AbstractNodeSection
from ..node_dialog_form import NodeDialogForm


class BreakLinkSection(AbstractNodeSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a BreakLink node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form, section_data=section_data, add_conversion_factor=False
        )
