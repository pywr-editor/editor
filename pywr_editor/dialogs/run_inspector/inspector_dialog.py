from typing import TYPE_CHECKING, Union

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QVBoxLayout
from pywr.core import Timestep
from pywr.model import Model

from pywr_editor.dialogs import InspectorTree
from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig
from pywr_editor.style import AppStylesheet
from pywr_editor.widgets import PushIconButton

if TYPE_CHECKING:
    from pywr_editor import MainWindow

"""
 Dialog to inspect the model results for a
 given timestep.
"""


class InspectorDialog(QDialog):
    def __init__(
        self,
        model_config: ModelConfig,
        pywr_model: Model,
        parent: Union[QWindow, "MainWindow", None] = None,
    ):
        """
        Initialises the dialog.
        :param model_config: The ModelConfig instance.
        :param pywr_model: The pywr Model instance.
        :param parent: The parent widget. Default to None.
        """
        super().__init__(parent)
        self.app = parent
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Dialog title
        # noinspection PyUnresolvedReferences
        timestep: Timestep = pywr_model.timestepper.current
        title = FormTitle(
            f"Model inspector - timestep {timestep.day}/{timestep.month}/"
            + f"{timestep.year}"
        )
        description = QLabel(
            "Inspect the values of the class attributes of the pywr model "
            + "for the current timestep"
        )
        description.setWordWrap(True)

        # inspector
        tree = InspectorTree(
            model_config=model_config, pywr_model=pywr_model, parent=self
        )

        # Buttons
        expand_all = PushIconButton(icon=qta.icon("msc.expand-all"), label="Expand all")
        # noinspection PyUnresolvedReferences
        expand_all.clicked.connect(tree.expandAll)
        collapse_all = PushIconButton(
            icon=qta.icon("msc.collapse-all"), label="Collapse all"
        )
        # noinspection PyUnresolvedReferences
        collapse_all.clicked.connect(tree.collapseAll)

        close_button = PushIconButton(icon=qta.icon("msc.close"), label="Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(expand_all)
        button_layout.addWidget(collapse_all)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(tree)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setWindowTitle("Model inspector")
        self.setMinimumSize(750, 650)
        self.setStyleSheet(AppStylesheet().get())
        self.setWindowModality(Qt.WindowModality.WindowModal)
        # always delete the dialog to release the model instance
        self.setAttribute(Qt.WA_DeleteOnClose)
