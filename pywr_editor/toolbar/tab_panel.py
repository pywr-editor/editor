from typing import TYPE_CHECKING, Literal

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QAction, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from pywr_editor.style import Color, stylesheet_dict_to_str

from .large_button import ToolbarLargeButton
from .small_button import ToolbarSmallButton

if TYPE_CHECKING:
    from .tab import Tab


class TabPanel(QWidget):
    def __init__(
        self,
        parent: "Tab",
        name: str,
        layout: Literal["horizontal", "vertical"],
        show_name: bool = True,
    ):
        """
        Initialises the panel for a tab containing the buttons.
        :param parent: The tab instance.
        :param name: The panel name.
        :param layout: Whether to organise the buttons in a horizontal or vertical
        layout.
        :param show_name: Whether to show the panel name.
        :return None.
        """
        super().__init__(parent=parent)
        self.setObjectName(f"toolbar_panel_{name}")
        self.buttons: dict[str, ToolbarLargeButton | ToolbarSmallButton] = {}
        self.widgets: list[QWidget] = []

        # load the panel style
        self.setStyleSheet(self.stylesheet)

        # create the layout containing the buttons/widgets
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # widget and layout containing the buttons and the panel name
        vertical_widget = QWidget(self)
        vertical_layout = QVBoxLayout()
        vertical_layout.setSpacing(0)
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        vertical_widget.setLayout(vertical_layout)

        # add button container widget and separator
        main_layout.addWidget(vertical_widget)
        main_layout.addWidget(TabPanelSeparator(self))

        # set the panel name
        label = QLabel(name)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f'color: {Color("gray", 500).hex}')

        # add to vertical layout the panel name and the button container
        actions_container_widget = QWidget(self)
        vertical_layout.addWidget(actions_container_widget)
        # add spacer when the buttons do not fill the panel completely
        if show_name:
            vertical_layout.addItem(
                QSpacerItem(10, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)
            )
            vertical_layout.addWidget(label)

        # layout containing the actions (buttons or other widgets)
        if layout == "horizontal":
            self.action_container_layout = QHBoxLayout()
        else:
            self.action_container_layout = QVBoxLayout()
        self.action_container_layout.setAlignment(Qt.AlignLeft)
        self.action_container_layout.setSpacing(0)
        self.action_container_layout.setContentsMargins(0, 0, 0, 0)

        actions_container_widget.setLayout(self.action_container_layout)

    def add_button(
        self, action: QAction, is_large: bool = True
    ) -> ToolbarSmallButton | ToolbarLargeButton:
        """
        Adds a new button widget to the panel.
        :param action: The action to attach to the button.
        :param is_large: Whether the button is larger or small.
        :return: The Button instance.
        """
        if is_large:
            button = ToolbarLargeButton(parent=self, action=action)
        else:
            button = ToolbarSmallButton(parent=self, action=action)

        self.action_container_layout.addWidget(button, 0, Qt.AlignTop)
        self.buttons[action.text()] = button

        return button

    def add_widget(self, widget: QWidget) -> None:
        """
        Adds a new button widget to the panel.
        :param widget: The widget to add.
        :return: None.
        """
        self.action_container_layout.addWidget(widget, 0, Qt.AlignTop)
        self.widgets.append(widget)

    def add_vertical_small_buttons(self, actions: list[QAction]) -> QWidget:
        """
        Adds a group of vertical small buttons to the panel.
        :param actions: The actions to attach to the buttons. A maximum of three
        buttons are allowed
        :return: The widget instance.
        """
        if len(actions) > 3:
            raise ValueError("A maximum of three buttons are allowed")

        layout = QVBoxLayout()
        self.action_container_layout.addLayout(layout)

        for action in actions:
            button = ToolbarSmallButton(parent=self, action=action)
            layout.addWidget(button, 0, Qt.AlignTop)
            self.buttons[action.text()] = button
        # add stretch in place of missing buttons
        for _ in range(0, 3 - len(actions)):
            layout.addStretch()
        return layout

    @property
    def stylesheet(self) -> str:
        """
        Defines the widget stylesheet.
        :return: The stylesheet as string.
        """
        style = {
            "QWidget": {
                "border": 0,
                "margin": 0,
                "padding": 0,
            }
        }

        return stylesheet_dict_to_str(style)


class TabPanelSeparator(QWidget):
    def __init__(self, parent: TabPanel):
        """
        Initialises the widget.
        :param parent: The tab panel to add the separator to.
        :return None
        """
        super().__init__(parent=parent)
        self.setMinimumHeight(90)
        self.setMaximumHeight(90)
        # control padding by changing the width
        self.setMinimumWidth(10)
        self.setMaximumWidth(10)
        self.setLayout(QHBoxLayout())

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Draws the separator.
        :param event: The paint event.
        :return: None
        """
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QPen(Color("gray", 300).qcolor))
        painter.drawLine(
            QPointF(self.width() / 2, 2),
            QPointF(self.width() / 2, self.height()),
        )
        painter.end()
