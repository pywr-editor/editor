from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMenu, QSizePolicy, QWidgetAction

from pywr_editor.style import AppStylesheet, stylesheet_dict_to_str


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
        return stylesheet_dict_to_str({"QMenu": AppStylesheet.misc()["QMenu"]})
