from typing import Type, TYPE_CHECKING, Union
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import (
    QDialog,
    QPushButton,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QWidget,
    QHBoxLayout,
)
from .node_dialog_form import NodeDialogForm
from pywr_editor.model import ModelConfig
from pywr_editor.node_shapes import (
    get_node_icon,
    get_pixmap_from_type,
    BaseNode,
)
from pywr_editor.form import FormTitle

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
        node_config = model_config.nodes.get_node_config_from_name(
            node_name=node_name, as_dict=False
        )
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Dialog title
        self.title = NodeDialogTitle(node_name, get_node_icon(node_config))

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Close
        )
        # noinspection PyTypeChecker
        save_button: QPushButton = button_box.findChild(QPushButton)
        save_button.setObjectName("save_button")
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(self.reject)

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
        layout.addWidget(button_box)

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
