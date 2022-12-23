from typing import Any

from pywr_editor.form import FloatWidget, FormSection, NodePickerWidget
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class AbstractStorageLicenseSection(FormSection):
    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict[str, Any],
        log_name: str,
        additional_fields: list[dict, Any] | None = None,
        amount_help_text: str | None = None,
    ):
        """
        Initialises a general form section for a license parameter inheriting
        from the StorageLicense parameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param log_name: The name of the log.
        :param additional_fields: A list of additional fields to add to the section.
        :param amount_help_text: The description to append to the amount field.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(log_name)

        if additional_fields:
            self.additional_fields = additional_fields
        else:
            self.additional_fields = []

        self.amount_help_text = "The total annual volume for this license"
        if amount_help_text:
            self.amount_help_text += f". {amount_help_text}"

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.form: ParameterDialogForm
        self.logger.debug("Registering form")

        data_dict = {
            "Configuration": [
                {
                    "name": "node",
                    "field_type": NodePickerWidget,
                    "value": self.form.get_param_dict_value("node"),
                    "help_text": "The node that uses the licence",
                },
                {
                    "name": "amount",
                    "label": "License amount",
                    "field_type": FloatWidget,
                    "allow_empty": False,
                    "value": self.form.get_param_dict_value("amount"),
                    "help_text": self.amount_help_text,
                },
            ]
            + self.additional_fields,
            "Miscellaneous": [
                {
                    "name": "comment",
                    "value": self.form.get_param_dict_value("comment"),
                },
            ],
        }

        return data_dict
