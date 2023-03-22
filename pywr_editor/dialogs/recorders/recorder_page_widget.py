from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig
from pywr_editor.utils import maybe_delete_component
from pywr_editor.widgets import PushButton

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

        # buttons
        close_button = PushButton("Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(parent.dialog.reject)

        # noinspection PyTypeChecker
        save_button = PushButton("Save recorder")
        save_button.setObjectName("save_button")

        add_button = PushButton("Add new recorder")
        add_button.setObjectName("add_button")
        # noinspection PyUnresolvedReferences
        add_button.clicked.connect(parent.on_add_new_recorder)

        delete_button = PushButton("Delete recorder")
        # noinspection PyUnresolvedReferences
        delete_button.clicked.connect(self.on_delete_recorder)

        button_box = QHBoxLayout()
        button_box.addWidget(save_button)
        button_box.addWidget(delete_button)
        button_box.addStretch()
        button_box.addWidget(add_button)
        button_box.addWidget(close_button)

        # form
        self.form = RecorderDialogForm(
            name=name,
            model_config=model_config,
            recorder_dict=self.recorder_dict,
            save_button=save_button,
            parent=self,
        )
        # noinspection PyUnresolvedReferences
        save_button.clicked.connect(self.form.on_save)

        layout.addWidget(self.title)
        layout.addWidget(self.form)
        layout.addLayout(button_box)

    def set_page_title(self, recorder_name: str) -> None:
        """
        Sets the page title.
        :param recorder_name: The recorder name.
        :return: None
        """
        self.title.setText(f"Recorder: {recorder_name}")

    @Slot()
    def on_delete_recorder(self) -> None:
        """
        Deletes the selected recorder.
        :return: None
        """
        dialog = self.pages.dialog
        list_widget = dialog.recorders_list_widget.list
        list_model = list_widget.model

        # check if recorder is being used and warn before deleting
        total_components = self.model_config.recorders.is_used(self.name)

        # ask before deleting
        if maybe_delete_component(self.name, total_components, self):
            # remove the recorder from the model
            # noinspection PyUnresolvedReferences
            list_model.layoutAboutToBeChanged.emit()
            list_model.recorder_names.remove(self.name)
            # noinspection PyUnresolvedReferences
            list_model.layoutChanged.emit()
            list_widget.clear_selection()

            # remove the page widget
            page_widget = self.pages.pages[self.name]
            page_widget.deleteLater()
            del self.pages.pages[self.name]

            # delete the recorder from the model configuration
            self.model_config.recorders.delete(self.name)

            # update tree and status bar
            if dialog.app is not None:
                if hasattr(dialog.app, "components_tree"):
                    dialog.app.components_tree.reload()
                if hasattr(dialog.app, "statusBar"):
                    dialog.app.statusBar().showMessage(
                        f'Deleted recorder "{self.name}"'
                    )

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        """
        Loads the form only when the page is requested.
        :param event: The event being triggered.
        :return: None
        """
        if self.form.loaded is False:
            self.form.load_fields()

        super().showEvent(event)
