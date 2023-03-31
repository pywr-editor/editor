from pywr_editor.form import (
    CheckSumWidget,
    FormSection,
    FormValidation,
    ScenarioPickerWidget,
    SourceSelectorWidget,
    UrlWidget,
)
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class DataFrameParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a DataFrameParameter.
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

        # Make field optional. Scenario cna be provided instead of column
        optional_col_field = self.form.column_field
        optional_col_field["field_args"] = {"optional": True}

        return {
            "Source": [
                self.form.source_field_wo_value,
                # table
                self.form.table_field,
                # anonymous table
                self.form.url_field,
            ]
            + self.form.csv_parse_fields
            + self.form.excel_parse_fields
            + self.form.h5_parse_fields,
            self.form.table_config_group_name: [
                self.form.index_col_field,
                self.form.parse_dates_field,
                optional_col_field,
                {
                    "name": "scenario",
                    "field_type": ScenarioPickerWidget,
                    "field_args": {"is_mandatory": False},
                    "value": self.form.get_param_dict_value("scenario"),
                    "help_text": "If you provide a scenario instead of a column, each "
                    "table column will be used as a scenario ensemble. The number of "
                    "columns must match the scenario size",
                },
            ],
            "Miscellaneous": [
                {
                    "name": "timestep_offset",
                    "label": "Time offset",
                    "field_type": "integer",
                    # default to 0 to remove the offset on save
                    "default_value": 0,
                    "value": self.form.get_param_dict_value("timestep_offset"),
                    "help_text": "When provided, the parameter will return the table "
                    + "value corresponding to the current model time-step plus or "
                    + "minus the offset. The offset can be used to look forward "
                    + "(when positive) or backward (when negative) in the table. "
                    + "If the offset takes the time index out of the data bounds, "
                    + "the parameter will return the first or last value available",
                },
                {
                    "name": "checksum",
                    "field_type": CheckSumWidget,
                    "value": self.form.get_param_dict_value("checksum"),
                    "help_text": "Validate the table file file using the provided "
                    "hash generated with the selected algorithm",
                },
                {
                    "name": "comment",
                    "value": self.form.get_param_dict_value("comment"),
                },
            ],
        }

    def validate(self, form_data: dict) -> FormValidation:
        """
        Validates the section/data after all the widgets are validated.
        :param form_data: The form data dictionary when the form validation is
        successful.
        :return: The FormValidation instance.
        """
        base_message = "You must select a column to use as a series or a "
        base_message += "scenario, to use the entire table"

        # the scenario or column must be provided
        if "scenario" not in form_data and "column" not in form_data:
            return FormValidation(validation=False, error_message=base_message)
        if "scenario" in form_data and "column" in form_data:
            return FormValidation(
                validation=False,
                error_message=f"{base_message}. You cannot select both options "
                "at the same time",
            )

        return FormValidation(validation=True)

    def filter(self, form_data: dict) -> None:
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

        keys_to_delete = ["source"]
        if form_data["source"] == labels["table"]:
            keys_to_delete += (
                ["url"]
                + UrlWidget.csv_fields
                + UrlWidget.excel_fields
                + UrlWidget.hdf_fields
                + UrlWidget.common_field
            )
        elif form_data["source"] == labels["anonymous_table"]:
            keys_to_delete += ["table"]

        self.logger.debug(f"Deleting keys: {keys_to_delete}")
        for key in keys_to_delete:
            form_data.pop(key, None)
