from typing import TYPE_CHECKING

from PySide6.QtWidgets import QPushButton

from pywr_editor.form import (
    FieldConfig,
    RecorderForm,
    RecorderTypeSelectorWidget,
    Validation,
)
from pywr_editor.model import ModelConfig
from pywr_editor.utils import Logging

if TYPE_CHECKING:
    from .recorder_page import RecorderPage


"""
 This forms allow editing a recorder
 configuration in the RecorderDialog widget.
"""


class RecorderDialogForm(RecorderForm):
    def __init__(
        self,
        name: str,
        model_config: ModelConfig,
        recorder_dict: dict,
        save_button: QPushButton,
        parent: "RecorderPage",
    ):
        """
        Initialises the recorder form.
        :param name: The recorder name.
        :param model_config: The ModelConfig instance.
        :param save_button: The button used to save the form.
        :param recorder_dict: The recorder configuration.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading with {recorder_dict}")

        self.name = name
        self.page = parent
        self.model_config = model_config
        self.recorder_dict = recorder_dict
        # noinspection PyTypeChecker
        self.dialog = self.page.pages.dialog

        self.recorder_obj = self.model_config.recorders.recorder(
            config=self.recorder_dict, deepcopy=True, name=name
        )
        available_fields = {
            "General": [
                FieldConfig(
                    name="name",
                    value=name,
                    help_text="A unique name identifying the recorder",
                    allow_empty=False,
                    validate_fun=self._check_recorder_name,
                ),
                FieldConfig(
                    name="type",
                    field_type=RecorderTypeSelectorWidget,
                    value=self.recorder_obj,
                ),
            ],
        }

        super().__init__(
            model_config=model_config,
            recorder_obj=self.recorder_obj,
            fields=available_fields,
            save_button=save_button,
            parent=parent,
        )

    def _check_recorder_name(self, name: str, label: str, value: str) -> Validation:
        """
        Checks that the new recorder name is not duplicated.
        :param name: The field name.
        :param label: The field label.
        :param value: The recorder name.
        :return: True if the name validates correctly, False otherwise.
        """
        # do not save form if the name is changed and already exists
        if self.name != value and self.model_config.recorders.exists(value) is True:
            return Validation(
                f'The recorder "{value}" already exists. '
                "Please provide a different name."
            )
        if self.name != value and self.model_config.parameters.exists(value) is True:
            return Validation(
                f'A parameter named "{value}" already exists. '
                "The name of model components must be unique. Please provide "
                "a different name.",
            )
        return Validation()
