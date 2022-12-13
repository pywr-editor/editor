from PySide6.QtWidgets import QStackedWidget
from typing import TYPE_CHECKING
from .recorder_empty_page_widget import RecorderEmptyPageWidget
from .recorder_page_widget import RecorderPageWidget
from pywr_editor.model import ModelConfig

if TYPE_CHECKING:
    from .recorders_dialog import RecordersDialog


class RecorderPagesWidget(QStackedWidget):
    def __init__(self, model_config: ModelConfig, parent: "RecordersDialog"):
        """
        Initialises the widget containing the pages to edit the recorders.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.model_config = model_config
        self.dialog = parent

        self.empty_page = RecorderEmptyPageWidget()
        self.addWidget(self.empty_page)

        self.pages = {}
        for name in model_config.recorders.get_all().keys():
            self.add_new_page(name)

        self.set_empty_page()

    def add_new_page(self, recorder_name: str) -> None:
        """
        Adds a new page.
        :param recorder_name: The page or recorder name.
        :return: None
        """
        self.pages[recorder_name] = RecorderPageWidget(
            name=recorder_name, model_config=self.model_config, parent=self
        )
        self.addWidget(self.pages[recorder_name])

    def rename_page(self, recorder_name: str, new_recorder_name: str) -> None:
        """
        Renames a page in the page dictionary.
        :param recorder_name: The recorder name to change.
        :param new_recorder_name: The new recorder name.
        :return: None
        """
        self.pages[new_recorder_name] = self.pages.pop(recorder_name)

    def set_empty_page(self) -> None:
        """
        Sets the empty page as visible.
        :return: None
        """
        self.setCurrentWidget(self.empty_page)

    def set_current_widget_by_name(self, recorder_name: str) -> bool:
        """
        Sets the current widget by providing the recorder name.
        :param recorder_name: The recorder name.
        :return: True if the recorder is found, False otherwise.
        """
        if recorder_name in self.pages.keys():
            self.setCurrentWidget(self.pages[recorder_name])
            return True
        return False
