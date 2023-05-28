from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig
from pywr_editor.utils import maybe_delete_component
from pywr_editor.widgets import PushIconButton

from .recorder_dialog_form import RecorderDialogForm
from .recorders_list_model import RecordersListModel

if TYPE_CHECKING:
    from ..base.component_pages import ComponentPages
    from .recorders_dialog import RecordersDialog


class RecorderPage(QWidget):
    def __init__(
        self,
        name: str,
        model: ModelConfig,
        pages: "ComponentPages",
    ):
        """
        Initialise the widget with the form to edit a recorder.
        :param name: The recorder name.
        :param model: The ModelConfig instance.
        :param pages: The parent widget containing the stacked pages.
        """
        super().__init__(pages)
        self.name = name
        self.pages = pages

        # noinspection PyTypeChecker
        self.dialog: "RecordersDialog" = pages.dialog
        self.model = model
        self.recorder_dict = model.recorders.config(name)

        # form title
        self.title = FormTitle()
        self.set_page_title(name)

        # buttons
        close_button = PushIconButton(icon="msc.close", label="Close")
        close_button.clicked.connect(self.dialog.reject)

        add_button = PushIconButton(icon="msc.add", label="Add new")
        add_button.setObjectName("add_button")
        add_button.clicked.connect(self.on_add_new_recorder)

        save_button = PushIconButton(icon="msc.save", label="Save", accent=True)
        save_button.setObjectName("save_button")
        save_button.clicked.connect(self.on_save_recorder)

        clone_button = PushIconButton(icon="msc.copy", label="Clone")
        clone_button.setToolTip(
            "Create a new recorder and copy this recorder's last saved configuration"
        )
        clone_button.setObjectName("clone_button")
        clone_button.clicked.connect(self.on_clone_recorder)

        delete_button = PushIconButton(icon="msc.remove", label="Delete")
        delete_button.setObjectName("delete_button")
        delete_button.clicked.connect(self.on_delete_recorder)

        button_box = QHBoxLayout()
        button_box.addWidget(add_button)
        button_box.addWidget(clone_button)
        button_box.addStretch()
        button_box.addWidget(save_button)
        button_box.addWidget(delete_button)
        button_box.addWidget(close_button)

        # form
        self.form = RecorderDialogForm(
            name=name,
            model_config=model,
            recorder_dict=self.recorder_dict,
            save_button=save_button,
            parent=self,
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.title)
        layout.addWidget(self.form)
        layout.addLayout(button_box)

    def set_page_title(self, recorder_name: str) -> None:
        """
        Set the page title.
        :param recorder_name: The recorder name.
        :return: None
        """
        self.title.setText(f"Recorder: {recorder_name}")

    @Slot()
    def on_add_new_recorder(self) -> None:
        """
        Slot called when user clicks on the "Add" button to insert a new recorder.
        :return: None
        """
        self.dialog.add_recorder()

    @Slot()
    def on_clone_recorder(self) -> None:
        """
        Clone the selected recorder.
        :return: None
        """
        self.dialog.add_recorder(self.model.recorders.config(self.name))

    @Slot()
    def on_save_recorder(self) -> None:
        """
        Slot called when user clicks on the "Update" button. Only visible fields
        are exported.
        :return: None
        """
        form_data = self.form.save()
        if form_data is False:
            return

        new_name = form_data["name"]
        if form_data["name"] != self.name:
            # update the model configuration
            self.model.recorders.rename(self.name, new_name)

            # update the page name in the list
            # noinspection PyUnresolvedReferences
            self.pages.rename_page(self.name, new_name)

            # update the page title
            self.set_page_title(new_name)

            # update the recorder list
            recorder_model: RecordersListModel = self.dialog.list_model
            idx = recorder_model.recorder_names.index(self.name)
            recorder_model.layoutAboutToBeChanged.emit()
            recorder_model.recorder_names[idx] = new_name
            recorder_model.layoutChanged.emit()

            self.name = new_name

        # update the model with the new dictionary
        del form_data["name"]
        self.model.recorders.update(self.name, form_data)

        # update the recorder list in case the name or the type (icon) need updating
        self.dialog.list.update()

        # update tree and status bar
        if self.dialog.app is not None:
            if hasattr(self.dialog.app, "components_tree"):
                self.dialog.app.components_tree.reload()
            if hasattr(self.dialog.app, "statusBar"):
                self.dialog.app.statusBar().showMessage(
                    f'Recorder "{self.name}" updated'
                )

    @Slot()
    def on_delete_recorder(self) -> None:
        """
        Deletes the selected recorder.
        :return: None
        """
        # check if recorder is being used and warn before deleting
        total_components = self.model.recorders.is_used(self.name)

        # ask before deleting
        if maybe_delete_component(self.name, total_components, self):
            # remove the recorder from the model
            self.dialog.list_model.layoutAboutToBeChanged.emit()
            self.dialog.list_model.recorder_names.remove(self.name)
            self.dialog.list_model.layoutChanged.emit()
            self.dialog.list.table.clear_selection()

            # remove the page widget
            # noinspection PyTypeChecker
            page: RecorderPage = self.pages.findChild(RecorderPage, self.name)
            page.deleteLater()
            # delete the recorder from the model configuration
            self.model.recorders.delete(self.name)
            # set default page
            self.pages.set_page_by_name("empty_page")

            # update tree and status bar
            if self.dialog.app is not None:
                if hasattr(self.dialog.app, "components_tree"):
                    self.dialog.app.components_tree.reload()
                if hasattr(self.dialog.app, "statusBar"):
                    self.dialog.app.statusBar().showMessage(
                        f'Deleted recorder "{self.name}"'
                    )

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        """
        Load the form only when the page is requested.
        :param event: The event being triggered.
        :return: None
        """
        if self.form.loaded_ is False:
            self.form.load_fields()

        super().showEvent(event)
