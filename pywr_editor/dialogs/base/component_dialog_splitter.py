from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QSplitter

from pywr_editor.dialogs.base.component_list import ComponentList
from pywr_editor.dialogs.base.component_pages import ComponentPages
from pywr_editor.style import Color, stylesheet_dict_to_str

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class ComponentDialogSplitter(QSplitter):
    def __init__(
        self,
        list_widget: ComponentList,
        pages_widget: ComponentPages,
        app: "MainWindow",
    ):
        """
        Initialise the splitter to split the list of components and the stacked pages.
        :param list_widget: The widget with the component list.
        :param pages_widget: The widget with the stacked component pages.
        :param app: The MainWindow instance.
        """
        super().__init__()
        if app:
            self.settings = app.editor_settings.instance
        else:
            self.settings = None

        # add the widgets
        self.addWidget(list_widget)
        self.addWidget(pages_widget)
        self.setCollapsible(0, False)
        self.handle(1).installEventFilter(self)

        # restore the state
        if self.settings:
            state = self.settings.value("window/component_splitter")
            self.restoreState(state)
        else:  # set minimum list widget width
            self.setSizes([280, 1000 - 280])
            list_min_size = list_widget.minimumWidth()
            self.setSizes([list_min_size, list_widget.dialog.width() - list_min_size])

        # style
        self.setOpaqueResize(True)
        self.setStyleSheet(
            stylesheet_dict_to_str(
                {
                    "ComponentDialogSplitter::handle": {
                        "width": "13px",
                        "background": Color("gray", 200).hex,
                    }
                }
            )
        )

    def eventFilter(
        self, watched: PySide6.QtCore.QObject, event: PySide6.QtCore.QEvent
    ) -> bool:
        """
        Save the splitter state after it is resized.
        :param watched: The watched object.
        :param event: The event instance.
        :return: Whether to filter the event.
        """
        if event.type() == QEvent.Type.MouseButtonRelease and self.settings:
            self.settings.setValue("window/component_splitter", self.saveState())

        return False
