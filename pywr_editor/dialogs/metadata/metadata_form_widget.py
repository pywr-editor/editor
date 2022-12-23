import re
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialogButtonBox

from pywr_editor.form import FieldConfig, Form, FormValidation
from pywr_editor.model import ModelConfig
from pywr_editor.utils import Logging

from .metadata_custom_fields_widget import MetadataCustomFieldsWidget

if TYPE_CHECKING:
    from .metadata_dialog import MetadataDialog


class MetadataFormWidget(Form):
    def __init__(
        self,
        model_config: ModelConfig,
        parent: "MetadataDialog",
    ):
        """
        Initialises the form.
        :param model_config: The ModelConfig instance.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.model_config = model_config
        self.dialog = parent
        self.logger.debug(f"Loading form with {self.model_config.metadata}")

        # custom fields data
        custom_fields = []
        for key, value in self.model_config.metadata.items():
            if key in [
                "title",
                "description",
                "minimum_version",
            ]:
                continue
            custom_fields.append([key, value])
            # custom_fields.append([humanise_label(key), value])

        available_fields: dict[str, list[FieldConfig]] = {
            "Basic information": [
                {
                    "name": "title",
                    "value": self.get_param_dict_value("title"),
                    "allow_empty": False,
                },
                {
                    "name": "description",
                    "value": self.get_param_dict_value("description"),
                },
                {
                    "name": "minimum_version",
                    "allow_empty": False,
                    "validate_fun": self._check_version_number,
                    "value": self.get_param_dict_value("minimum_version"),
                },
            ],
            "Custom fields": [
                {
                    "name": "custom_fields",
                    "hide_label": True,
                    "field_type": MetadataCustomFieldsWidget,
                    "value": custom_fields,
                }
            ],
        }

        super().__init__(
            available_fields=available_fields,
            save_button=parent.button_box.button(
                QDialogButtonBox.StandardButton.Save
            ),
            parent=parent,
        )

        # save form with button click
        # noinspection PyUnresolvedReferences
        parent.button_box.accepted.connect(self.on_save)

    @staticmethod
    def _check_version_number(
        name: str, label: str, value: str
    ) -> FormValidation:
        """
        Checks the minimum version number field.
        :param name: The field name
        :param label: The field label.
        :param value: The field value.
        :return: The FormValidation instance.
        """
        matches = re.findall(r"\b\d+(?:\.\d+)+", value)
        if matches:
            return FormValidation(validation=True)
        else:
            return FormValidation(
                validation=False,
                error_message="You must provide a valid minimum version of Pywr",
            )

    def get_param_dict_value(self, key: str) -> Any:
        """
        Gets a value from the metadata configuration.
        :param key: The key to extract the value of.
        :return: The value or empty if the key is not set.
        """
        return super().get_dict_value(key, self.model_config.metadata)

    @Slot()
    def on_save(self) -> None:
        """
        Slot called when user clicks on the "Update" button. Only visible fields are
         exported.
        :return: None
        """
        self.logger.debug("Saving form")

        form_data = self.validate()
        if form_data is False:
            self.logger.debug("Validation failed")
            return

        # merge custom fields
        custom_fields = form_data.pop("custom_fields", {})
        form_data = {**form_data, **custom_fields}

        # update model dictionary
        self.logger.debug(f"Updated metadata with {form_data}")
        self.model_config.json["metadata"] = form_data
        self.model_config.changes_tracker.add(
            f"Updated model metadata to {form_data}"
        )

        # reload the components tree
        if self.dialog.parent is not None:
            self.dialog.parent.components_tree.reload()
            self.dialog.parent.statusBar().showMessage(
                "Successfully updated the model metadata"
            )
