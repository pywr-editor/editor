from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu, QLabel, QSizePolicy, QWidgetAction
from pywr_editor.style import Color, stylesheet_dict_to_str


class ContextualMenu(QMenu):
    def __init__(self):
        """
        Initialises the widget.
        """
        super().__init__()
        self.setStyleSheet(self.stylesheet)

        # disable default frame and background
        # noinspection PyUnresolvedReferences
        self.setWindowFlags(self.windowFlags() | Qt.NoDropShadowWindowHint)

    def set_title(self, label: str) -> None:
        """
        Sets the menu title.
        :param label: The title.
        :return: None
        """
        max_size = 20
        if len(label) > max_size:
            label = f"{label[0:max_size]}..."
        title = QLabel(label)
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        title_action = QWidgetAction(self)
        title_action.setDefaultWidget(title)
        self.addAction(title_action)

    @property
    def stylesheet(self) -> str:
        """
        Returns the style.
        :return: The stylesheet as string.
        """
        return stylesheet_dict_to_str(
            {
                "QMenu": {
                    "background": Color("gray", 100).hex,
                    "border": f'1px solid {Color("gray", 300).hex}',
                    "border-radius": "6px",
                    "color": Color("gray", 600).hex,
                    "padding": "5px",
                    "margin": 0,
                    "::separator": {
                        "background": Color("gray", 300).hex,
                        "margin": "5px 1px",
                        "height": "1px",
                    },
                    "::item": {
                        "background-color": "transparent",
                        "border": f'1px solid {Color("gray", 100).hex}',
                        "padding": "4px 20px",
                        "::selected, ::pressed": {
                            "background-color": Color("blue", 200).hex,
                            "border": f'1px solid {Color("blue", 300).hex}',
                            "border-radius": "6px",
                            "color": Color("gray", 700).hex,
                        },
                        "::disabled": {
                            "color": Color("gray", 400).hex,
                        },
                        # title
                        "QLabel": {
                            "color": Color("gray", 600).hex,
                            "font-weight": "bold",
                            "padding": "4px 18px",
                        },
                    },
                },
            }
        )
