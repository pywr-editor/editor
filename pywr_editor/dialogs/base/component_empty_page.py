from PySide6.QtCore import Slot
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from pywr_editor.dialogs.base.component_pages import ComponentPages
from pywr_editor.form import FormTitle
from pywr_editor.style import Color
from pywr_editor.widgets import PushIconButton


class ComponentEmptyPage(QWidget):
    def __init__(
        self,
        title: str,
        description: str,
        icon_resource_name: str,
        pages: ComponentPages,
    ):
        """
        Initialise the empty page widget.
        :param title: The page title.
        :param description: The page description.
        :param icon_resource_name: The name of the resource containing the SVG icon.
        :param pages: The parent stacked widget.
        """
        super().__init__(pages)
        self.pages = pages

        dialog = pages.parent()
        layout = QVBoxLayout(self)
        page_title = FormTitle(title)

        page_description = QLabel()
        page_description.setText(description)
        page_description.setStyleSheet(f"color :{Color('gray', 500).hex}")
        page_description.setWordWrap(True)

        icon_layout = QHBoxLayout()
        icon_layout.addSpacerItem(
            QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
        icon = QSvgWidget(icon_resource_name)
        icon.setFixedSize(200, 200)
        icon_layout.addWidget(icon)

        # buttons
        close_button = PushIconButton(icon="msc.close", label="Close")
        close_button.clicked.connect(dialog.reject)

        add_button = PushIconButton(icon="msc.add", label="Add new", accent=True)
        add_button.setObjectName("add_button")
        add_button.clicked.connect(self.on_add_new_component)

        button_box = QHBoxLayout()
        button_box.addWidget(add_button)
        button_box.addStretch()
        button_box.addWidget(close_button)

        layout.addWidget(page_title)
        layout.addLayout(icon_layout)
        layout.addWidget(page_description)
        layout.addSpacerItem(
            QSpacerItem(10, 30, QSizePolicy.Expanding, QSizePolicy.Expanding)
        )
        layout.addLayout(button_box)
        close_button.setFocus()

    @Slot()
    def on_add_new_component(self) -> None:
        """
        Virtual method that is executed when the user clicks on the add button to
        add a new component. This method, once reimplemented, should call the
        action to add a new parameter, table or recorder.
        :return: None
        """
        raise NotImplementedError
