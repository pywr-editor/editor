from typing import TYPE_CHECKING, Union

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout

from pywr_editor.model import ModelConfig
from pywr_editor.widgets import PushIconButton

from .metadata_form_widget import MetadataFormWidget

if TYPE_CHECKING:
    from pywr_editor import MainWindow


class MetadataDialog(QDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        parent: Union["MainWindow", None] = None,
    ):
        """
        Initialises the modal dialog.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.parent = parent
        self.model_config = model_config
        self.setAttribute(Qt.WA_DeleteOnClose)

        # dialog buttons
        # Buttons
        button_box = QHBoxLayout()
        self.save_button = PushIconButton(
            icon=qta.icon("msc.save"), label="Save"
        )
        self.save_button.setObjectName("save_button")

        close_button = PushIconButton(icon=qta.icon("msc.close"), label="Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(self.reject)

        button_box.addStretch()
        button_box.addWidget(self.save_button)
        button_box.addWidget(close_button)

        # form
        self.form = MetadataFormWidget(model_config=model_config, parent=self)
        self.form.load_fields()
        self.form.setMinimumHeight(350)

        # set layout
        layout = QVBoxLayout()
        layout.addWidget(self.form)
        layout.addLayout(button_box)
        self.setLayout(layout)

        self.setWindowTitle("Model metadata")
        self.setMinimumSize(600, 600)
        self.setMaximumSize(600, 600)
        self.setWindowModality(Qt.WindowModality.WindowModal)
