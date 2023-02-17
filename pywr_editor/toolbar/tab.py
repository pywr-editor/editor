from typing import TYPE_CHECKING, Literal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QWidget

from .tab_panel import TabPanel

if TYPE_CHECKING:
    from .toolbar import ToolbarWidget


class Tab(QWidget):
    def __init__(self, parent: "ToolbarWidget", name: str):
        """
        Initialises the toolbar tab.
        :param parent: The toolbar widget.
        :param name: The tab name.
        :return None
        """
        super().__init__(parent=parent)
        self.setObjectName(f"toolbar_tab_{name}")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        self.panels: dict[str, TabPanel] = {}

        # layout containing the panels
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft)

    def add_panel(
        self,
        name: str,
        show_name: bool = True,
        layout: Literal["horizontal", "vertical"] = "horizontal",
    ) -> TabPanel:
        """
        Adds the panel container to the tab.
        :param name: The tab name.
        :param show_name: Whether to show the panel name.
        :param layout: Whether to organise the buttons in a horizontal or vertical
        layout. Default to horizontal.
        :return: The panel instance.
        """
        panel = TabPanel(self, name, layout, show_name)
        self.layout().addWidget(panel)
        self.panels[name] = panel

        return panel
