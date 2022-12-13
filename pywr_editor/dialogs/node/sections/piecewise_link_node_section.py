from .abstract_piecewise_link_node_section import (
    AbstractPiecewiseLinkNodeSection,
)
from ..node_dialog_form import NodeDialogForm


class PiecewiseLinkSection(AbstractPiecewiseLinkNodeSection):
    def __init__(self, form: NodeDialogForm, section_data: dict):
        """
        Initialises the form section for a PiecewiseLink node.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            log_name=self.__class__.__name__,
        )
