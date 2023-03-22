from typing import TYPE_CHECKING

from PySide6.QtCore import QUuid, Slot
from PySide6.QtWidgets import QStackedWidget

from pywr_editor.model import ModelConfig

from .recorder_empty_page_widget import RecorderEmptyPageWidget
from .recorder_page_widget import RecorderPageWidget

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

        self.empty_page = RecorderEmptyPageWidget(self)
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

    @Slot()
    def on_add_new_recorder(self) -> None:
        """
        Adds a new recorder. This creates a new scenario in the model and adds, and
        selects the form page.
        :return: None
        """
        list_widget = self.dialog.recorders_list_widget.list
        list_model = self.dialog.recorders_list_widget.model
        proxy_model = self.dialog.recorders_list_widget.proxy_model

        # generate unique name
        recorder_name = f"Recorder {QUuid().createUuid().toString()[1:7]}"

        # add the dictionary to the model. Default to NodeRecorder
        # NOTE: the node is not specified and the recorder is not valid
        self.model_config.recorders.update(recorder_name, {"type": "node"})

        # add the page
        pages_widget: RecorderPagesWidget = self.dialog.pages_widget
        pages_widget.add_new_page(recorder_name)
        pages_widget.set_current_widget_by_name(recorder_name)

        # add it to the list model
        # noinspection PyUnresolvedReferences
        list_model.layoutAboutToBeChanged.emit()
        list_model.recorder_names.append(recorder_name)
        # noinspection PyUnresolvedReferences
        list_model.layoutChanged.emit()
        # select the item
        new_index = proxy_model.mapFromSource(
            list_widget.find_index_by_name(recorder_name)
        )
        list_widget.setCurrentIndex(new_index)

        # update tree and status bar
        if self.dialog.app is not None:
            if hasattr(self.dialog.app, "components_tree"):
                self.dialog.app.components_tree.reload()
            if hasattr(self.dialog.app, "statusBar"):
                self.dialog.app.statusBar().showMessage(
                    f'Added new recorder "{recorder_name}"'
                )
