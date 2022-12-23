from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QPushButton

from pywr_editor.form import (
    FormValidation,
    ParameterForm,
    ParameterTypeSelectorWidget,
)
from pywr_editor.model import ModelConfig
from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from .parameter_page_widget import ParameterPageWidget
    from .parameters_list_model import ParametersListModel

"""
 This forms allow editing a parameter
 configuration in the ParameterDialog widget.
"""


class ParameterDialogForm(ParameterForm):
    def __init__(
        self,
        name: str,
        model_config: ModelConfig,
        parameter_dict: dict,
        save_button: QPushButton,
        parent: "ParameterPageWidget",
    ):
        """
        Initialises the parameter form.
        :param name: The parameter name.
        :param model_config: The ModelConfig instance.
        :param save_button: The button used to save the form.
        :param parameter_dict: The parameter configuration.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading with {parameter_dict}")

        self.name = name
        self.page = parent
        self.model_config = model_config
        self.parameter_dict = parameter_dict
        # noinspection PyTypeChecker
        self.dialog = self.page.pages.dialog

        self.parameter_obj = self.model_config.parameters.parameter(
            config=self.parameter_dict, deepcopy=True, name=name
        )
        available_fields = {
            "General": [
                {
                    "name": "name",
                    "value": name,
                    "help_text": "A unique name identifying the parameter",
                    "allow_empty": False,
                    "validate_fun": self._check_parameter_name,
                },
                {
                    "name": "type",
                    "field_type": ParameterTypeSelectorWidget,
                    "value": self.parameter_obj,
                },
            ],
        }

        super().__init__(
            model_config=model_config,
            parameter_obj=self.parameter_obj,
            available_fields=available_fields,
            save_button=save_button,
            parent=parent,
        )

    def _check_parameter_name(
        self, name: str, label: str, value: str
    ) -> FormValidation:
        """
        Checks that the new parameter name is not duplicated.
        :param name: The field name.
        :param label: The field label.
        :param value: The parameter name.
        :return: True if the name validates correctly, False otherwise.
        """
        # do not save form if the name is changed and already exists
        if (
            self.name != value
            and self.model_config.parameters.does_parameter_exist(value) is True
        ):
            return FormValidation(
                validation=False,
                error_message=f"A parameter named '{value}' already exists. "
                + "Please provide a different name.",
            )
        if (
            self.name != value
            and self.model_config.recorders.does_recorder_exist(value) is True
        ):
            return FormValidation(
                validation=False,
                error_message=f"A recorder named '{value}' already exists. "
                + "The name of model components must be unique. Please provide "
                + "a different name.",
            )
        return FormValidation(validation=True)

    @Slot()
    def on_save(self) -> None:
        """
        Slot called when user clicks on the "Update" button. Only visible fields are
        exported.
        :return: None
        """
        self.logger.debug("Saving form")

        form_data = self.save()
        if form_data is False:
            return

        new_name = form_data["name"]
        if form_data["name"] != self.name:
            # update the model configuration
            self.model_config.parameters.rename(self.name, new_name)

            # update the page name in the list
            # noinspection PyUnresolvedReferences
            self.page.pages.rename_page(self.name, new_name)

            # update the page title
            self.page.set_page_title(new_name)

            # update the parameter list
            parameter_model: "ParametersListModel" = (
                self.page.pages.dialog.parameters_list_widget.model
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
        self.dialog.parameters_list_widget.update()

        # update tree and status bar
        app = self.dialog.app
        if app is not None:
            if hasattr(app, "components_tree"):
                app.components_tree.reload()
            if hasattr(app, "statusBar"):
                app.statusBar().showMessage(f'Parameter "{self.name}" updated')
