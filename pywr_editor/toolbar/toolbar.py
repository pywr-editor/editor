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
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        # self.toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self.setMovable(False)
        self.addWidget(self.toolbar)

        self.setVisible(True)
        self.show()

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
                    "background": Color("gray", 80).hex,
                    "border-radius": 0,
                    "margin": 0,
                    "padding": 0,
                },
                "::tab-bar": {"left": "5px"},
            },
            "QTabBar": {
                "::tab": {
                    "border-bottom": "1px solid transparent",
                    "color": Color("gray", 600).hex,
                    "font-size": "13px",
                    "margin-right": "5px",
                    "padding-bottom": "4px",
                    "padding-right": "12px",
                    "padding-left": "12px",
                    "padding-top": " 4px",
                },
                "::tab:hover": {
                    "background": Color("gray", 100).hex,
                    "border-bottom": f"1px solid {Color('gray', 400).hex}",
                },
                "::tab:selected": {
                    "border-bottom": f"3px solid {Color('blue', 400).hex}",
                    "color": Color("gray", 700).hex,
                    "font-weight": "bold",
                },
            },
        }

        return stylesheet_dict_to_str(style)
