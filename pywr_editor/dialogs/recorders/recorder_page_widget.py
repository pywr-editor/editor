from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig

from .recorder_dialog_form import RecorderDialogForm

if TYPE_CHECKING:
    from .recorder_pages_widget import RecorderPagesWidget


class RecorderPageWidget(QWidget):
    def __init__(
        self,
        name: str,
        model_config: ModelConfig,
        parent: "RecorderPagesWidget",
    ):
        """
        Initialises the widget with the form to edit a recorder.
        :param name: The recorder name.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.name = name
        self.pages = parent
        self.model_config = model_config
        self.recorder_dict = model_config.recorders.get_config_from_name(name)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # form title
        self.title = FormTitle()
        self.set_page_title(name)

        # button
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
            | QDialogButtonBox.StandardButton.Save
        )
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(parent.dialog.reject)
        # noinspection PyTypeChecker
        save_button: QPushButton = button_box.findChild(QPushButton)
        save_button.setObjectName("save_button")
        save_button.setText("Update recorder")

        # form
        self.form = RecorderDialogForm(
            name=name,
            model_config=model_config,
            recorder_dict=self.recorder_dict,
            save_button=save_button,
            parent=self,
        )
        # noinspection PyUnresolvedReferences
        button_box.accepted.connect(self.form.on_save)

        layout.addWidget(self.title)
        layout.addWidget(self.form)
        layout.addWidget(button_box)

    def set_page_title(self, recorder_name: str) -> None:
        """
        Sets the page title.
        :param recorder_name: The recorder name.
        :return: None
        """
        self.title.setText(f"Recorder: {recorder_name}")

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        """
        Loads the form only when the page is requested.
        :param event: The event being triggered.
        :return: None
        """
        if self.form.loaded is False:
            self.form.load_fields()

        super().showEvent(event)
