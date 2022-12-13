from ..parameter_dialog_form import ParameterDialogForm
from pywr_editor.form import (
    FloatWidget,
    SourceSelectorWidget,
    ValueWidget,
    UrlWidget,
    FormSection,
)
from pywr_editor.utils import Logging


class ConstantParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a CustomParameter.
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

        data_dict = {
            "Source": [
                self.form.source_field,
                {
                    # widget handles "value" and "values" keys, but form returns
                    # "value" as key
                    "name": "value",
                    "field_type": ValueWidget,
                    "value": {
                        "values": self.form.get_param_dict_value("values"),
                        "value": self.form.get_param_dict_value("value"),
                    },
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
                self.form.parse_dates_field,
                # fields for table and anonymous table
                self.form.column_field,
                self.form.index_field,
            ],
            "Miscellaneous": [
                {
                    "name": "offset",
                    "value": self.form.get_param_dict_value("offset"),
                    "field_type": FloatWidget,
                    "default_value": None,
                    "help_text": "Offset the constant value by the provided amount. "
                    + "Default to empty to ignore",
                },
                {
                    "name": "scale",
                    "field_type": FloatWidget,
                    "default_value": None,
                    "value": self.form.get_param_dict_value("scale"),
                    "help_text": "Scale the constant value by the provided amount. "
                    + "Default to empty to ignore",
                },
                {
                    "name": "comment",
                    "value": self.form.get_param_dict_value("comment"),
                },
            ],
            self.form.optimisation_config_group_name: [
                self.form.is_variable_field,
                {
                    "name": "lower_bounds",
                    "field_type": FloatWidget,
                    "value": self.form.get_param_dict_value("lower_bounds"),
                    "help_text": "The smallest value for the parameter during "
                    + "optimisation",
                },
                {
                    "name": "upper_bounds",
                    "field_type": FloatWidget,
                    "value": self.form.get_param_dict_value("upper_bounds"),
                    "help_text": "The largest value for the parameter during "
                    + "optimisation",
                },
            ],
        }

        # disable optimisation section
        if self.section_data["enable_optimisation_section"] is False:
            del data_dict[self.form.optimisation_config_group_name]

        return data_dict

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
        url_fields = (
            UrlWidget.csv_fields
            + UrlWidget.excel_fields
            + UrlWidget.hdf_fields
            + UrlWidget.common_field
        )

        if form_data["source"] == labels["table"]:
            keys_to_delete += ["value", "url"] + url_fields
        elif form_data["source"] == labels["anonymous_table"]:
            keys_to_delete += ["value", "table"]
        # default
        else:
            keys_to_delete += ["table", "index", "column", "url"] + url_fields

        self.logger.debug(f"Deleting keys: {keys_to_delete}")
        for key in keys_to_delete:
            form_data.pop(key, None)
