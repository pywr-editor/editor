from typing import TYPE_CHECKING

from PySide6.QtCore import Slot

from ..base.component_empty_page import ComponentEmptyPage

if TYPE_CHECKING:
    from ..base.component_pages import ComponentPages
    from .tables_dialog import TablesDialog


class TableEmptyPage(ComponentEmptyPage):
    def __init__(self, pages: "ComponentPages"):
        """
        Initialise the empty page widget.
        :param pages: The parent widget containing the page stack.
        """
        super().__init__(
            "Tables",
            "Select the table you would like to edit on the list on the left-hand "
            "side. Otherwise click the 'Add' button to add a new table to the model "
            "configuration.",
            ":misc/table-dialog",
            pages,
        )

    @Slot()
    def on_add_new_component(self) -> None:
        # noinspection PyTypeChecker
        dialog: "TablesDialog" = self.pages.dialog
        dialog.add_table()
