from typing import TYPE_CHECKING

from PySide6.QtCore import Slot

from ..base.component_empty_page import ComponentEmptyPage

if TYPE_CHECKING:
    from ..base.component_pages import ComponentPages
    from .recorders_dialog import RecordersDialog


class RecorderEmptyPage(ComponentEmptyPage):
    def __init__(self, pages: "ComponentPages"):
        """
        Initialise the empty page widget.
        :param pages: The parent widget containing the page stack.
        """
        super().__init__(
            "Recorders",
            "Select the model recorder you would like to edit on the list on the left"
            "-hand side. Otherwise click the 'Add' button to add a new recorder to "
            "the model configuration.",
            ":toolbar/edit-recorders",
            pages,
        )

    @Slot()
    def on_add_new_component(self) -> None:
        # noinspection PyTypeChecker
        dialog: "RecordersDialog" = self.pages.dialog
        dialog.add_recorder()
