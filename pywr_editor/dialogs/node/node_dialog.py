from typing import TYPE_CHECKING, Type, Union

import qtawesome as qta
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig
from pywr_editor.node_shapes import (
    BaseNode,
    get_node_icon,
    get_pixmap_from_type,
)

from ...widgets import PushIconButton
from .node_dialog_form import NodeDialogForm

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class NodeDialog(QDialog):
    def __init__(
        self,
        node_name: str,
        model_config: ModelConfig,
        parent: Union[QWindow, "MainWindow", None] = None,
    ):
        """
        Initialises the modal dialog.
        :param node_name: The selected node name.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.app = parent
        node_config = model_config.nodes.config(node_name=node_name, as_dict=False)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Dialog title
        self.title = NodeDialogTitle(node_name, get_node_icon(node_config))

        # Buttons
        button_box = QHBoxLayout()
        save_button = PushIconButton(icon=qta.icon("msc.save"), label="Save")
        save_button.setObjectName("save_button")

        close_button = PushIconButton(icon=qta.icon("msc.close"), label="Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(self.reject)

        button_box.addStretch()
        button_box.addWidget(save_button)
        button_box.addWidget(close_button)

        # Form
        self.form = NodeDialogForm(
            node_dict=node_config.props,
            model_config=model_config,
            save_button=save_button,
            parent=self,
        )
        # noinspection PyUnresolvedReferences
        save_button.clicked.connect(self.form.save)

        layout.addWidget(self.title)
        layout.addWidget(self.form)
        layout.addLayout(button_box)

        self.setLayout(layout)
        self.setWindowTitle(f"Edit node - {node_name}")
        self.setMinimumSize(750, 650)
        self.setWindowModality(Qt.WindowModality.WindowModal)


class NodeDialogTitle(QWidget):
    # fit all node icons
    icon_size = QSize(30, 27)

    def __init__(self, node_name: str, node_icon_type: Type[BaseNode]):
        """
        Initialises the class to display the dialog title with the node icon.
        :param node_name: The node name to display in the title.
        :param node_icon_type: The class type for the node icon.
        """
        super().__init__()
        self.title = FormTitle(node_name)

        self.icon = QLabel()
        icon, icon_name = get_pixmap_from_type(self.icon_size, node_icon_type)
        self.icon.setPixmap(icon)
        self.icon.setObjectName(icon_name)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.icon)
        layout.addWidget(self.title)
        layout.addStretch()

    def update_name(self, node_name: str) -> None:
        """
        Updates the node name.
        :param node_name: The name of the node.
        :return: None
        """
        self.title.setText(node_name)

    def update_icon(self, node_icon_type: Type[BaseNode]) -> None:
        """
        Updates the icon.
        :param node_icon_type: The class type for the node icon.
        :return: None
        """
        icon, icon_name = get_pixmap_from_type(self.icon_size, node_icon_type)
        self.icon.setPixmap(icon)
        self.icon.setObjectName(icon_name)
