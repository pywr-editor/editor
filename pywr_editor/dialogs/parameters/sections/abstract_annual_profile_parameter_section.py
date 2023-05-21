from pywr_editor.form import (
    AbstractAnnualValuesModel,
    AbstractFloatListWidget,
    FormSection,
    FormValidation,
    SourceSelectorWidget,
    UrlWidget,
)
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm

"""
  Abstract section class to use for annual profile
  parameters.
"""


class AbstractAnnualProfileParameterSection(FormSection):
    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict,
        values_widget: AbstractAnnualValuesModel,
        opt_widget: AbstractFloatListWidget,
        log_name: str,
    ):
        """
        Initialises the form section for a weekly profile parameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param values_widget: The widget to use to handle the profile values.
        :param opt_widget: The widget to use to handle the optimisation bounds.
        :param log_name: The name to use in the logger.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.logger = Logging().logger(log_name)
        self.total_values = values_widget.total_values

        # Make field optionals. At least one of them must be provided depending on how
        # the profile is selected in the table (by row or by column). See self.validate
        optional_col_field = self.form.column_field
        optional_col_field["field_args"] = {"optional": True}

        optional_index_field = self.form.index_field
        optional_index_field["field_args"] = {"optional": True}

        self.form_dict = {
            "Source": [
                self.form.source_field,
                {
                    "name": "values",
                    "field_type": values_widget,
                    "value": self.form.get_param_dict_value("values"),
                    "allow_empty": False,
                },
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
                optional_index_field,
                optional_col_field,
            ],
            "Miscellaneous": [self.form.comment],
            self.form.optimisation_config_group_name: [
                self.form.is_variable_field,
                {
                    "name": "lower_bounds",
                    "field_type": opt_widget,
                    "value": self.form.get_param_dict_value("lower_bounds"),
                    "help_text": "The smallest value for the parameter during "
                    + "optimisation. This can be a number, to use the same bound "
                    + f"for all {self.total_values} values, or {self.total_values} "
                    + "comma-separated values to bound each value",
                },
                {
                    "name": "upper_bounds",
                    "field_type": opt_widget,
                    "value": self.form.get_param_dict_value("upper_bounds"),
                    "help_text": "The largest value for the parameter during "
                    + "optimisation. This can be a number, to use the same bound "
                    + f"for all {self.total_values} values, or {self.total_values} "
                    + "comma-separated values to bound each value",
                },
            ],
        }

        # disable optimisation section
        if self.section_data["enable_optimisation_section"] is False:
            del self.form_dict[self.form.optimisation_config_group_name]

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.logger.debug("Registering form")

        return self.form_dict

    def validate(self, form_data):
        """
        Validates the section/data after all the widgets are validated.
        :param form_data: The form data dictionary when the form validation is
        successful.
        :return: The FormValidation instance.
        """
        # noinspection PyTypeChecker
        source_widget: SourceSelectorWidget = self.form.find_field_by_name(
            "source"
        ).widget
        labels = source_widget.labels

        # ignore fields when values are provided
        if form_data["source"] != labels["value"]:
            # keys with empty values have been already removed
            if "column" not in form_data and "index" not in form_data:
                return FormValidation(
                    validation=False,
                    error_message="To define a profile you must select an index or "
                    + "column name",
                )
            if "column" in form_data and "index" in form_data:
                return FormValidation(
                    validation=False,
                    error_message="You must select an index value (to select a table "
                    + "row) or a column name (to select a table column). You cannot "
                    + "select both at the same time",
                )

        return FormValidation(validation=True)

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

        url_fields = (
            UrlWidget.csv_fields
            + UrlWidget.excel_fields
            + UrlWidget.hdf_fields
            + UrlWidget.common_field
        )

        keys_to_delete = ["source"]
        if form_data["source"] == labels["table"]:
            keys_to_delete += ["values", "url"] + url_fields
        elif form_data["source"] == labels["anonymous_table"]:
            keys_to_delete += ["values", "table"]
        # default
        else:
            keys_to_delete += ["table", "index", "url"] + url_fields

        self.logger.debug(f"Deleting keys: {keys_to_delete}")
        for key in keys_to_delete:
            form_data.pop(key, None)
