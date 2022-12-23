from pywr_editor.form import (
    FormSection,
    ScenarioPickerWidget,
    ScenarioValuesWidget,
    SourceSelectorWidget,
    UrlWidget,
    ValuesAndExternalDataWidget,
)
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class ArrayIndexedScenarioMonthlyFactorsParameterSection(FormSection):
    def __init__(self, form: ParameterDialogForm, section_data: dict):
        """
        Initialises the form section for a ArrayIndexedScenarioMonthlyFactorsParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(self.__class__.__name__)
        self.data_dict = {}

    @property
    def data(self):
        """
        Defines the section data dictionary.
        :return: The section dictionary.
        """
        self.form: ParameterDialogForm
        self.logger.debug("Registering form")
        total_model_steps = self.form.model_config.number_of_steps

        self.data_dict = {
            "Configuration": [
                {
                    "name": "scenario",
                    "field_type": ScenarioPickerWidget,
                    "value": self.form.get_param_dict_value("scenario"),
                },
                {
                    # do not use "values" to avoid conflict with source field below
                    # field is renamed to "values" in filter
                    "name": "ts_values",
                    "label": "Timestep values",
                    "field_type": ValuesAndExternalDataWidget,
                    "value": self.form.get_param_dict_value("values"),
                    "field_args": {
                        "show_row_numbers": True,
                        "row_number_label": "Timestep number",
                        "variable_names": "Value",
                        "min_total_values": total_model_steps
                        if total_model_steps is not None
                        else None,
                    },
                    "help_text": "Provides the timeseries values to be perturbed using "
                    "the monthly factors below in each ensemble",
                },
            ],
            "Factors": [
                self.form.source_field,
                {
                    "name": "values",
                    "field_type": ScenarioValuesWidget,
                    "field_args": {"data_type": "monthly_profile"},
                    "value": self.form.get_param_dict_value("factors"),
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
            "Miscellaneous": [
                {
                    "name": "comment",
                    "value": self.form.get_param_dict_value("comment"),
                },
            ],
        }

        return self.data_dict

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

        # remove unnecessary keys depending on source for factors
        keys_to_delete = []
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

        # if factors is provided as value, use list
        if source == labels["value"]:
            form_data["factors"] = form_data["values"]
            del form_data["values"]
        # otherwise use dictionary. Collect all the fields in the factor section
        else:
            form_data["factors"] = {}
            for field_dict in self.data_dict["Factors"]:
                name = field_dict["name"]
                if name not in form_data:
                    continue
                form_data["factors"][name] = form_data[name]
                del form_data[name]

        # rename ts_values to values
        form_data["values"] = form_data["ts_values"]
        del form_data["ts_values"]
