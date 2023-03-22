from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig
from pywr_editor.utils import maybe_delete_component
from pywr_editor.widgets import PushButton

from .parameter_dialog_form import ParameterDialogForm

if TYPE_CHECKING:
    from .parameter_pages_widget import ParameterPagesWidget


class ParameterPageWidget(QWidget):
    def __init__(
        self,
        name: str,
        model_config: ModelConfig,
        parent: "ParameterPagesWidget",
    ):
        """
        Initialises the widget with the form to edit a parameter.
        :param name: The parameter name.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.name = name
        self.pages = parent
        self.model_config = model_config
        self.parameter_dict = model_config.parameters.get_config_from_name(name)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # form title
        self.title = FormTitle()
        self.set_page_title(name)

        # buttons
        close_button = PushButton("Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(parent.dialog.reject)

        add_button = PushButton("Add new parameter")
        add_button.setObjectName("add_button")
        # noinspection PyUnresolvedReferences
        add_button.clicked.connect(parent.on_add_new_parameter)

        save_button = PushButton("Save parameter")
        save_button.setObjectName("save_button")

        delete_button = PushButton("Delete parameter")
        delete_button.setObjectName("delete_button")
        # noinspection PyUnresolvedReferences
        delete_button.clicked.connect(self.on_delete_parameter)

        button_box = QHBoxLayout()
        button_box.addWidget(save_button)
        button_box.addWidget(delete_button)
        button_box.addStretch()
        button_box.addWidget(add_button)
        button_box.addWidget(close_button)

        # form
        self.form = ParameterDialogForm(
            name=name,
            model_config=model_config,
            parameter_dict=self.parameter_dict,
            save_button=save_button,
            parent=self,
        )
        # noinspection PyUnresolvedReferences
        save_button.clicked.connect(self.form.on_save)

        layout.addWidget(self.title)
        layout.addWidget(self.form)
        layout.addLayout(button_box)

    def set_page_title(self, parameter_name: str) -> None:
        """
        Sets the page title.
        :param parameter_name: The parameter name.
        :return: None
        """
        self.title.setText(f"Parameter: {parameter_name}")

    @Slot()
    def on_delete_parameter(self) -> None:
        """
        Deletes the selected parameter.
        :return: None
        """
        dialog = self.pages.dialog
        list_widget = dialog.parameters_list_widget.list
        list_model = list_widget.model
        # check if parameter is being used and warn before deleting
        total_components = self.model_config.parameters.is_used(self.name)

        # ask before deleting
        if maybe_delete_component(self.name, total_components, self):
            # remove the parameter from the model
            # noinspection PyUnresolvedReferences
            list_model.layoutAboutToBeChanged.emit()
            list_model.parameter_names.remove(self.name)
            # noinspection PyUnresolvedReferences
            list_model.layoutChanged.emit()
            list_widget.clear_selection()

            # remove the page widget
            page_widget = dialog.pages_widget.pages[self.name]
            page_widget.deleteLater()
            del dialog.pages_widget.pages[self.name]

            # delete the parameter from the model configuration
            self.model_config.parameters.delete(self.name)

            # update tree and status bar
            if dialog.app is not None:
                if hasattr(dialog.app, "components_tree"):
                    dialog.app.components_tree.reload()
                if hasattr(dialog.app, "statusBar"):
                    dialog.app.statusBar().showMessage(
                        f'Deleted parameter "{self.name}"'
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
