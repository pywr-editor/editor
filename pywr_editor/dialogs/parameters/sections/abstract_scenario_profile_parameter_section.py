from typing import Any, Literal

from pywr_editor.form import (
    FieldConfig,
    FormSection,
    ScenarioPickerWidget,
    ScenarioValuesWidget,
    SourceSelectorWidget,
    UrlWidget,
)
from pywr_editor.utils import Logging

from ..parameter_dialog_form import ParameterDialogForm


class AbstractScenarioProfileParameterSection(FormSection):
    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict[str, Any],
        profile_type: Literal["daily", "weekly", "monthly"],
        log_name: str,
    ):
        """
        Initialises the form section for a ScenarioMonthlyProfileParameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param profile_type: The profile type. It can be one of the following: daily,
        weekly or monthly.
        :param log_name: The name of the log.
        """
        super().__init__(form, section_data)
        self.logger = Logging().logger(log_name)
        self.profile_type = profile_type

        self.form: ParameterDialogForm
        self.add_fields(
            {
                "Configuration": [
                    FieldConfig(
                        name="scenario",
                        field_type=ScenarioPickerWidget,
                        value=self.form.field_value("scenario"),
                    ),
                ],
                "Source": [
                    self.form.source_field,
                    FieldConfig(
                        name="values",
                        field_type=ScenarioValuesWidget,
                        field_args={"data_type": f"{self.profile_type}_profile"},
                        value=self.form.field_value("values"),
                    ),
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
        )

    def filter(self, form_data):
        """
        Removes fields depending on the value set in source.
        :param form_data: The form data dictionary.
        :return: None.
        """
        # noinspection PyTypeChecker
        source_widget: SourceSelectorWidget = self.form.find_field("source").widget
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
