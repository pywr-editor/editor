from pywr_editor.form import (
    FormSection,
    ScenarioPickerWidget,
    ScenarioValuesWidget,
    SourceSelectorWidget,
    UrlWidget,
)
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class ArrayIndexedScenarioParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a ArrayIndexedScenarioParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(self.__class__.__name__)

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.form: ParameterDialogForm
        self.logger.debug("Registering form")

        return {
            "Configuration": [
                {
                    "name": "scenario",
                    "field_type": ScenarioPickerWidget,
                    "value": self.form.get_param_dict_value("scenario"),
                },
                self.form.source_field,
                {
                    "name": "values",
                    "field_type": ScenarioValuesWidget,
                    "field_args": {"data_type": "timestep_series"},
                    "value": self.form.get_param_dict_value("values"),
                    "help_text": "Provide one value for each model timestep",
                },
                # table
                self.form.table_field,
                # anonymous table
                self.form.url_field,
            ]
            + self.form.csv_parse_fields
            + self.form.excel_parse_fields
            + self.form.h5_parse_fields
            + [self.form.index_col_field],
            "Miscellaneous": [self.form.comment],
        }

    def filter(self, form_data):
        """
        Removes fields depending on the value set in source.
        :param form_data: The form data dictionary.
        :return: None.
        """
        # noinspection PyTypeChecker
        source_widget: SourceSelectorWidget = self.form.find_field_by_name(
            "source"
        ).widget
        labels = source_widget.labels

        # remove unnecessary keys depending on source for factors
        url_fields = (
            UrlWidget.csv_fields
            + UrlWidget.excel_fields
            + UrlWidget.hdf_fields
            + UrlWidget.common_field
        )

        source = form_data["source"]
        keys_to_delete = ["source"]
        if source == labels["table"]:
            keys_to_delete += ["values", "url"] + url_fields
        elif source == labels["anonymous_table"]:
            keys_to_delete += ["values", "table"]
        # default
        else:
            keys_to_delete += ["table", "index", "url"] + url_fields

        self.logger.debug(f"Deleting keys: {keys_to_delete}")
        for key in keys_to_delete:
            form_data.pop(key, None)
