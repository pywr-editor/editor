from typing import TYPE_CHECKING

import PySide6
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from pywr_editor.form import FormTitle
from pywr_editor.model import ModelConfig
from pywr_editor.utils import maybe_delete_component
from pywr_editor.widgets import PushIconButton

from .parameter_dialog_form import ParameterDialogForm

if TYPE_CHECKING:
    from ..base.component_pages import ComponentPages
    from .parameters_dialog import ParametersDialog
    from .parameters_list_model import ParametersListModel


class ParameterPage(QWidget):
    def __init__(
        self,
        name: str,
        model: ModelConfig,
        pages: "ComponentPages",
    ):
        """
        Initialises the widget with the form to edit a parameter.
        :param name: The parameter name.
        :param model: The ModelConfig instance.
        :param pages: The parent widget containing the stacked pages.
        """
        super().__init__(pages)
        self.name = name
        self.pages = pages

        # noinspection PyTypeChecker
        self.dialog: "ParametersDialog" = pages.dialog
        self.model = model
        self.parameter_dict = model.parameters.config(name)

        # form title
        self.title = FormTitle()
        self.set_page_title(name)

        # buttons
        close_button = PushIconButton(icon="msc.close", label="Close")
        close_button.clicked.connect(self.dialog.reject)

        add_button = PushIconButton(icon="msc.add", label="Add new")
        add_button.setObjectName("add_button")
        add_button.clicked.connect(self.on_add_new_parameter)

        save_button = PushIconButton(icon="msc.save", label="Save", accent=True)
        save_button.setObjectName("save_button")
        save_button.clicked.connect(self.on_save_parameter)

        clone_button = PushIconButton(icon="msc.copy", label="Clone")
        clone_button.setToolTip(
            "Create a new parameter and copy this parameter's last saved configuration"
        )
        clone_button.setObjectName("clone_button")
        clone_button.clicked.connect(self.on_clone_parameter)

        delete_button = PushIconButton(icon="msc.remove", label="Delete")
        delete_button.setObjectName("delete_button")
        delete_button.clicked.connect(self.on_delete_parameter)

        button_box = QHBoxLayout()
        button_box.addWidget(add_button)
        button_box.addWidget(clone_button)
        button_box.addStretch()
        button_box.addWidget(save_button)
        button_box.addWidget(delete_button)
        button_box.addWidget(close_button)

        #  form
        self.form = ParameterDialogForm(
            name=name,
            model_config=model,
            parameter_dict=self.parameter_dict,
            save_button=save_button,
            parent=self,
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.title)
        layout.addWidget(self.form)
        layout.addLayout(button_box)

    def set_page_title(self, parameter_name: str) -> None:
        """
        Set the page title.
        :param parameter_name: The parameter name.
        :return: None
        """
        self.title.setText(f"Parameter: {parameter_name}")

    @Slot()
    def on_add_new_parameter(self) -> None:
        """
        Slot called when user clicks on the "Add" button to insert a new parameter.
        :return: None
        """
        self.dialog.add_parameter()

    @Slot()
    def on_clone_parameter(self) -> None:
        """
        Slot called when user clicks on the "Clone" button to clone an existing
        parameter.
        :return: None
        """
        self.dialog.add_parameter(self.model.parameters.config(self.name))

    @Slot()
    def on_save_parameter(self) -> None:
        """
        Slot called when user clicks on the "Save" button.
        :return: None
        """
        form_data = self.form.save()
        if form_data is False:
            return

        new_name = form_data["name"]
        if form_data["name"] != self.name:
            # update the model configuration
            self.model.parameters.rename(self.name, new_name)
            # update the page name in the list
            self.pages.rename_page(self.name, new_name)
            # update the page title
            self.set_page_title(new_name)

            # update the parameter list
            parameter_model: "ParametersListModel" = self.dialog.list_model
            idx = parameter_model.parameter_names.index(self.name)
            parameter_model.layoutAboutToBeChanged.emit()
            parameter_model.parameter_names[idx] = new_name
            parameter_model.layoutChanged.emit()

            self.name = new_name

        # update the model with the new dictionary
        del form_data["name"]
        self.model.parameters.update(self.name, form_data)

        # update the parameter list in case the name or the type (icon) need updating
        self.dialog.list.update()

        # update tree and status bar
        if self.dialog.app is not None:
            if hasattr(self.dialog.app, "components_tree"):
                self.dialog.app.components_tree.reload()
            if hasattr(self.dialog.app, "statusBar"):
                self.dialog.app.statusBar().showMessage(
                    f'Parameter "{self.name}" updated'
                )

    @Slot()
    def on_delete_parameter(self) -> None:
        """
        Deletes the selected parameter.
        :return: None
        """
        # check if parameter is being used and warn before deleting
        total_components = self.model.parameters.is_used(self.name)

        # ask before deleting
        if maybe_delete_component(self.name, total_components, self):
            # remove the parameter from the model
            self.dialog.list_model.layoutAboutToBeChanged.emit()
            self.dialog.list_model.parameter_names.remove(self.name)
            self.dialog.list_model.layoutChanged.emit()
            self.dialog.list.table.clear_selection()

            # remove the page widget
            # noinspection PyTypeChecker
            page: ParameterPage = self.pages.findChild(ParameterPage, self.name)
            page.deleteLater()
            # delete the parameter from the model configuration
            self.model.parameters.delete(self.name)
            # set default page
            self.pages.set_page_by_name("empty_page")

            # update tree and status bar
            if self.dialog.app is not None:
                if hasattr(self.dialog.app, "components_tree"):
                    self.dialog.app.components_tree.reload()
                if hasattr(self.dialog.app, "statusBar"):
                    self.dialog.app.statusBar().showMessage(
                        f'Deleted parameter "{self.name}"'
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
