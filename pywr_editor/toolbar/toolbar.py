from PySide6.QtWidgets import QToolBar, QTabWidget, QMainWindow
from .tab import Tab
from pywr_editor.style import Color, stylesheet_dict_to_str


class ToolbarWidget(QToolBar):
    def __init__(self, parent: QMainWindow):
        """
        Initialises the ribbon widget.
        :param parent: The parent widget.
        """
        super().__init__(parent)

        # load the toolbar style
        self.setStyleSheet(self.stylesheet)
        self.tabs = {}

        self.setObjectName("toolbar")
        self.toolbar = QTabWidget(self)
        self.toolbar.setMaximumHeight(120)
        self.toolbar.setMinimumHeight(110)
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
                    "background-color": Color("gray", 100).hex,
                    # 'border-bottom': f'1px solid {Color("gray", 300).hex}',
                    "border-top": f'1px solid {Color("gray", 300).hex}',
                    "border-radius": 0,
                    "margin": 0,
                    "padding": 0,
                    "top": "-1",
                },
                "::tab-bar": {"left": "5px"},
            },
            "QTabBar": {
                "::tab": {
                    # 'border-radius': 0,
                    "border-top-left-radius": "4px",
                    "border-top-right-radius": "4px",
                    "color": Color("gray", 600).hex,
                    "margin-right": "5px",
                    "padding-bottom": "4px",
                    "padding-right": "12px",
                    "padding-left": "12px",
                    "padding-top": " 4px",
                },
                "::tab#toolbar_tab_Model": {"background": "yellow"},
                "::tab:hover": {
                    "background": Color("gray", 50).hex,
                    "border": f'1px solid {Color("gray", 200).hex}',
                    "border-bottom-color": Color("gray", 300).hex,
                },
                "::tab:selected": {
                    "background": Color("gray", 100).hex,
                    "border": f'1px solid {Color("gray", 300).hex}',
                    "border-bottom-color": Color("gray", 100).hex,
                    "color": Color("gray", 700).hex,
                },
            },
        }

        return stylesheet_dict_to_str(style)
