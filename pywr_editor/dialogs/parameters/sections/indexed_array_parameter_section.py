from pywr_editor.form import (
    FormSection,
    ParameterLineEditWidget,
    ParametersListPickerWidget,
)
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class IndexedArrayParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a IndexedArrayParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        self.form: ParameterDialogForm

        super().__init__(form, section_data)
        self.logger = Logging().logger(self.__class__.__name__)
        self.model_config = self.form.model_config

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.form: ParameterDialogForm
        self.logger.debug("Registering form")

        # parameter supports two keys
        parameter_values = self.form.get_param_dict_value("params")
        if parameter_values is None:
            parameter_values = self.form.get_param_dict_value("parameters")

        data_dict = {
            "Configuration": [
                {
                    "name": "parameters",
                    "field_type": ParametersListPickerWidget,
                    "value": parameter_values,
                    "help_text": "This parameter returns the value of one of the "
                    + "parameter above based on the Index parameter below. If the "
                    + "index parameter returns 0, the first parameter value from the "
                    + "list above is used",
                },
                {
                    "name": "index_parameter",
                    "field_type": ParameterLineEditWidget,
                    "field_args": {
                        "include_param_key": self.model_config.pywr_parameter_data.get_keys_with_parent_class(  # noqa: E501
                            "IndexParameter"
                        )
                        + self.model_config.includes.get_keys_with_subclass(
                            "IndexParameter", "parameter"
                        ),
                    },
                    "value": self.form.get_param_dict_value("index_parameter"),
                },
            ],
            "Miscellaneous": [
                {
                    "name": "comment",
                    "value": self.form.get_param_dict_value("comment"),
                },
            ],
        }

        return data_dict
