from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QDialogButtonBox,
    QWidget,
)
from pywr_editor.style import Color, stylesheet_dict_to_str
from .table_view import TableView
from .push_icon_button import PushIconButton

"""
 Creates a dialog to edit the model settings
 with an horizontal layout. The layout needs
 to contain a TableView widget with buttons on
 the left and another widget on the right.
"""


class SettingsDialog(QDialog):
    def __init__(
        self,
        parent: QWidget = None,
    ):
        """
        Initialises the modal dialog.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModality.WindowModal)

    def setup(self, left_widget: QWidget, right_widget: QWidget) -> None:
        """
        Setups the window with the widgets.
        :param left_widget: The widget to add to the left side of the dialog layout.
        :param right_widget: The widget to add to the left side of the dialog layout.
        :return: None
        """
        # dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(self.reject)
        button_box.setStyleSheet("margin-bottom:10px")

        # list + form layout
        right_layout = QVBoxLayout()
        right_layout.addWidget(right_widget)
        right_layout.addWidget(button_box)

        # modal layout
        modal_layout = QHBoxLayout()
        modal_layout.setContentsMargins(0, 0, 20, 0)
        # modal_layout.setSpacing(0)
        modal_layout.addWidget(left_widget)
        modal_layout.addLayout(right_layout)
        self.setLayout(modal_layout)

        # Re-style the components
        # set the left widget background
        left_widget.setAttribute(Qt.WA_StyledBackground, True)
        left_widget.setStyleSheet(
            self.left_widget_stylesheet(left_widget.__class__.__name__)
        )

        # change the style of the buttons interacting with the menu
        for button in left_widget.findChildren(PushIconButton):
            button.setStyleSheet(self.menu_buttons_stylesheet)

        # change the menu style
        left_widget.layout().setContentsMargins(10, 20, 10, 20)
        # noinspection PyTypeChecker
        menu: TableView = left_widget.findChild(TableView)
        menu.verticalHeader().setDefaultSectionSize(30)
        menu.setStyleSheet(self.menu_stylesheet)

    @staticmethod
    def left_widget_stylesheet(widget_name: str) -> str:
        """
        Returns the style to apply to the widget on the left side of the layout.
        :param widget_name: The widget name.
        :return: The stylesheet.
        """
        return stylesheet_dict_to_str(
            {
                widget_name: {
                    "background-color": Color("gray", 50).hex,
                    "border-top": f'1px solid {Color("gray", 200).hex}',
                    "border-right": f'1px solid {Color("gray", 200).hex}',
                }
            }
        )

    @property
    def menu_stylesheet(self) -> str:
        """
        Returns the style to apply to the TableView within the left widget.
        :return: The stylesheet.
        """
        stylesheet: dict = TableView.stylesheet(as_string=False)
        stylesheet["TableView"]["background"] = "transparent"
        stylesheet["TableView"]["border"] = 0
        stylesheet["TableView"]["border-top"] = "1px solid transparent"
        stylesheet["TableView"]["border-bottom"] = "1px solid transparent"
        stylesheet["TableView"]["::item"]["border-radius"] = "5px"

        return stylesheet_dict_to_str(stylesheet)

    @property
    def menu_buttons_stylesheet(self) -> str:
        """
        Returns the style to apply to the TableView buttons within the left widget.
        :return: The stylesheet.
        """
        return stylesheet_dict_to_str(
            {
                "PushIconButton": {
                    "background": "transparent",
                    "border": 0,
                    "padding": "15px 10px",
                    "padding-bottom": 0,
                    # "margin-top": "15px",
                    "font-size": "14px",
                    ":hover": {
                        "color": Color("blue", 400).hex,
                    },
                }
            }
        )
