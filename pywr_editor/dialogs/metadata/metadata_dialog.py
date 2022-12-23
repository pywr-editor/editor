from typing import TYPE_CHECKING, Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from pywr_editor.model import ModelConfig

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
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Close
        )
        # noinspection PyUnresolvedReferences
        self.button_box.rejected.connect(self.reject)

        # form
        self.form = MetadataFormWidget(model_config=model_config, parent=self)
        self.form.load_fields()
        self.form.setMinimumHeight(350)

        # set layout
        layout = QVBoxLayout()
        layout.addWidget(self.form)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.setWindowTitle("Model metadata")
        self.setMinimumSize(600, 600)
        self.setMaximumSize(600, 600)
        self.setWindowModality(Qt.WindowModality.WindowModal)
