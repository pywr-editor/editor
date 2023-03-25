from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QTabWidget, QToolBar

from pywr_editor.style import Color, stylesheet_dict_to_str

from .tab import Tab


class ToolbarWidget(QToolBar):
    def __init__(self, parent: QMainWindow):
        """
        Initialises the ribbon widget.
        :param parent: The parent widget.
        """
        super().__init__(parent)

        # load the toolbar style
        self.setStyleSheet(self.stylesheet)
        self.tabs: dict[str, Tab] = {}

        self.setObjectName("toolbar")
        self.toolbar = QTabWidget(self)
        self.toolbar.setMaximumHeight(125)
        self.toolbar.setMinimumHeight(110)
        self.toolbar.setContextMenuPolicy(
            Qt.ContextMenuPolicy.PreventContextMenu
        )
        self.setMovable(False)
        self.addWidget(self.toolbar)

    def add_tab(self, name: str) -> Tab:
        """
        Adds a new tab to the toolbar.
        :param name: The tab name.
        :return: The tab instance.
        """
        tab = Tab(parent=self, name=name)
        self.toolbar.addTab(tab, name)
        self.tabs[name] = tab

        return tab

    @property
    def stylesheet(self) -> str:
        """
        Defines the widget stylesheet.
        :return: The stylesheet as string.
        """
        style = {
            "QToolBar": {"padding": 0},
            "QTabWidget": {
                ":pane": {
                    "background-color": Color("gray", 200).hex,
                    "border-top": f'1px solid {Color("gray", 400).hex}',
                    "border-radius": 0,
                    "margin": 0,
                    "padding": 0,
                    "top": "-1px",
                },
                "::tab-bar": {"left": "5px"},
            },
            "QTabBar": {
                "::tab": {
                    "border-top-left-radius": "4px",
                    "border-top-right-radius": "4px",
                    "color": Color("gray", 600).hex,
                    "margin-right": "5px",
                    "padding-bottom": "4px",
                    "padding-right": "12px",
                    "padding-left": "12px",
                    "padding-top": " 4px",
                },
                "::tab:hover": {
                    "background": Color("gray", 100).hex,
                    "border": f'1px solid {Color("gray", 300).hex}',
                    "border-bottom-color": Color("gray", 400).hex,
                },
                "::tab:selected": {
                    "background": Color("gray", 200).hex,
                    "border": f'1px solid {Color("gray", 400).hex}',
                    "border-bottom-color": Color("gray", 200).hex,
                    "color": Color("gray", 700).hex,
                    "margin-bottom": "-1px",
                },
            },
        }

        return stylesheet_dict_to_str(style)
