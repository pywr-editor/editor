from typing import TYPE_CHECKING

from PySide6.QtWidgets import QPushButton

from pywr_editor.form import FormValidation, ParameterForm, ParameterTypeSelectorWidget
from pywr_editor.model import ModelConfig
from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from .parameter_page_widget import ParameterPageWidget

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
        if self.name != value and self.model_config.parameters.exists(value) is True:
            return FormValidation(
                validation=False,
                error_message=f"A parameter named '{value}' already exists. "
                + "Please provide a different name.",
            )
        if self.name != value and self.model_config.recorders.exists(value) is True:
            return FormValidation(
                validation=False,
                error_message=f"A recorder named '{value}' already exists. "
                + "The name of model components must be unique. Please provide "
                + "a different name.",
            )
        return FormValidation(validation=True)
