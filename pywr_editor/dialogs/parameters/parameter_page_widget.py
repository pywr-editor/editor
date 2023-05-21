from typing import TYPE_CHECKING

import PySide6
import qtawesome as qta
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig
from pywr_editor.utils import maybe_delete_component
from pywr_editor.widgets import PushIconButton

from .parameter_dialog_form import ParameterDialogForm

if TYPE_CHECKING:
    from .parameter_pages_widget import ParameterPagesWidget
    from .parameters_list_model import ParametersListModel


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
        self.parameter_dict = model_config.parameters.config(name)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # form title
        self.title = FormTitle()
        self.set_page_title(name)

        # buttons
        close_button = PushIconButton(icon=qta.icon("msc.close"), label="Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(parent.dialog.reject)

        add_button = PushIconButton(icon=qta.icon("msc.add"), label="Add new")
        add_button.setObjectName("add_button")
        # noinspection PyUnresolvedReferences
        add_button.clicked.connect(parent.on_add_new_parameter)

        save_button = PushIconButton(icon=qta.icon("msc.save"), label="Save")
        save_button.setObjectName("save_button")
        # noinspection PyUnresolvedReferences
        save_button.clicked.connect(self.on_save)

        clone_button = PushIconButton(icon=qta.icon("msc.copy"), label="Clone")
        clone_button.setToolTip(
            "Create a new parameter and copy this parameter's last saved configuration"
        )
        clone_button.setObjectName("clone_button")
        # noinspection PyUnresolvedReferences
        clone_button.clicked.connect(self.on_clone_parameter)

        delete_button = PushIconButton(icon=qta.icon("msc.remove"), label="Delete")
        delete_button.setObjectName("delete_button")
        # noinspection PyUnresolvedReferences
        delete_button.clicked.connect(self.on_delete_parameter)

        button_box = QHBoxLayout()
        button_box.addWidget(add_button)
        button_box.addWidget(clone_button)
        button_box.addStretch()
        button_box.addWidget(save_button)
        button_box.addWidget(delete_button)
        button_box.addWidget(close_button)

        # form
        self.form = ParameterDialogForm(
            name=name,
            model_config=model_config,
            parameter_dict=self.parameter_dict,
            save_button=save_button,
            parent=self,
        )

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
    def on_save(self) -> None:
        """
        Slot called when user clicks on the "Save" button. Only visible fields are
        exported.
        :return: None
        """
        form_data = self.form.save()
        if form_data is False:
            return

        new_name = form_data["name"]
        if form_data["name"] != self.name:
            # update the model configuration
            self.model_config.parameters.rename(self.name, new_name)

            # update the page name in the list
            # noinspection PyUnresolvedReferences
            self.pages.rename_page(self.name, new_name)

            # update the page title
            self.set_page_title(new_name)

            # update the parameter list
            parameter_model: "ParametersListModel" = (
                self.pages.dialog.parameters_list_widget.model
            )
            idx = parameter_model.parameter_names.index(self.name)
            # noinspection PyUnresolvedReferences
            parameter_model.layoutAboutToBeChanged.emit()
            parameter_model.parameter_names[idx] = new_name

            # noinspection PyUnresolvedReferences
            parameter_model.layoutChanged.emit()

            self.name = new_name

        # update the model with the new dictionary
        del form_data["name"]
        self.model_config.parameters.update(self.name, form_data)

        # update the parameter list in case the name or the type (icon) need updating
        self.pages.dialog.parameters_list_widget.update()

        # update tree and status bar
        app = self.pages.dialog.app
        if app is not None:
            if hasattr(app, "components_tree"):
                app.components_tree.reload()
            if hasattr(app, "statusBar"):
                app.statusBar().showMessage(f'Parameter "{self.name}" updated')

    @Slot()
    def on_clone_parameter(self) -> None:
        """
        Clones the selected parameter.
        :return: None
        """
        self.pages.on_add_new_parameter(self.model_config.parameters.config(self.name))

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
            page_widget = self.pages.pages[self.name]
            page_widget.deleteLater()
            del self.pages.pages[self.name]

            # delete the parameter from the model configuration
            self.model_config.parameters.delete(self.name)

            # set default page
            self.pages.set_empty_page()

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
