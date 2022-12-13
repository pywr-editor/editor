from PySide6.QtCore import Qt
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QGroupBox,
    QLabel,
)
from typing import TYPE_CHECKING, Union
from .edge_slots_widget import EdgeSlotsWidget
from pywr_editor.form import FormTitle, Form, FieldConfig
from pywr_editor.model import ModelConfig

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class EdgeSlotsDialog(QDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        parent: Union[QWindow, "MainWindow", None] = None,
    ):
        """
        Initialises the dialog.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.app = parent
        self.model_config = model_config
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Dialog title
        title = FormTitle("Edit edge slots")
        description = QLabel(
            "Customise the slot names for the nodes in the edges. The name can be "
            + "set for certain node types (such as the 'Storage' or 'Multi split "
            + "link' node) and can be an integer or a string depending on the node "
            + "you would like to customise"
        )
        description.setWordWrap(True)

        # Button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(self.reject)

        # Form
        fields: dict[str, list[FieldConfig]] = {
            "Slots": [
                {
                    "name": "slots",
                    "field_type": EdgeSlotsWidget,
                    "value": model_config.edges,
                    "hide_label": True,
                }
            ]
        }
        form = Form(
            available_fields=fields,
            parent=self,
            direction="vertical",
        )
        form.load_fields()

        # remove group box title
        # noinspection PyTypeChecker
        first_section: QGroupBox = form.findChild(QGroupBox, "Slots")
        first_section.setTitle("")
        first_section.setStyleSheet(
            "QGroupBox{border:0;padding:0;padding-top:15px; margin-top:-15px}"
        )

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(form)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setWindowTitle("Edit edge slots")
        self.setMinimumSize(750, 650)
