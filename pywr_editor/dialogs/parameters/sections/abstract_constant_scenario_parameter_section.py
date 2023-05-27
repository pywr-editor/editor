from typing import Any, Type

from PySide6.QtCore import Slot

from pywr_editor.form import (
    FieldConfig,
    FormSection,
    ScenarioPickerWidget,
    SourceSelectorWidget,
    TableValuesWidget,
    UrlWidget,
    Validation,
)
from pywr_editor.utils import Logging, get_signal_sender

from ..parameter_dialog_form import ParameterDialogForm

"""
  Abstract section class to use for ConstantScenarioParameter
  and ConstantScenarioIndexParameter
"""


class AbstractConstantScenarioParameterSection(FormSection):
    def __init__(
        self,
        form: ParameterDialogForm,
        section_data: dict,
        values_widget: Type[TableValuesWidget],
        values_widget_options: dict[str, Any],
        log_name: str,
    ):
        """
        Initialises the form section for a weekly profile parameter.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param values_widget: An instance of TableValuesWidget.
        :param values_widget_options: The options to pass to TableValuesWidget as
        dictionary.
        :param log_name: The name to use in the logger.
        """
        super().__init__(form, section_data)
        self.form: ParameterDialogForm

        self.logger = Logging().logger(log_name)
        self.values_widget_options = values_widget_options

        if "exact_total_values" not in self.values_widget_options:
            raise ValueError(
                "You must provide the 'exact_total_values' property in "
                + "'values_widget_options'"
            )

        # Make fields optional. At least one of them must be provided depending
        # on how the profile is selected in the table (by row or by column).
        # See self.validate
        optional_col_field = self.form.column_field
        optional_col_field["field_args"] = {"optional": True}

        optional_index_field = self.form.index_field
        optional_index_field["field_args"] = {"optional": True}

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
                        field_type=values_widget,
                        field_args=values_widget_options,
                        value={
                            "values": self.form.field_value("values"),
                        },
                    ),
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
            }
        )

        self.form.register_after_render_action(self.register_scenario_change)

    def register_scenario_change(self) -> None:
        """
        Registers a slot to notify when the scenario name is changed.
        :return: None
        """
        form_field = self.form.find_field("scenario")
        # noinspection PyTypeChecker
        widget: ScenarioPickerWidget = form_field.widget
        # noinspection PyUnresolvedReferences
        widget.combo_box.currentIndexChanged.connect(self._update_scenario_size)

    @Slot()
    def _update_scenario_size(self) -> None:
        """
        Updates the TableValuesWidget exact_total_values property when a new scenario
        is selected.
        :return: None
        """
        self.logger.debug(
            f"Running _update_scenario_size Slot from {get_signal_sender(self)}"
        )
        self.form: "ParameterDialogForm"

        scenario_field = self.form.find_field("scenario")
        values_field = self.form.find_field("values")
        values_widget: TableValuesWidget = values_field.widget

        scenario = scenario_field.value()
        if scenario is not None:
            scenario_size = self.form.model_config.scenarios.config(
                scenario, as_dict=False
            ).size

            self.logger.debug(f"Setting exact_total_values to {scenario_size}")
            values_widget.exact_total_values = scenario_size
        else:
            values_widget.exact_total_values = None

    def validate(self, form_data):
        # noinspection PyTypeChecker
        source_widget: SourceSelectorWidget = self.form.find_field("source").widget
        labels = source_widget.labels

        # check external data
        if form_data["source"] != labels["value"]:
            # keys with empty values have been already removed
            if "column" not in form_data and "index" not in form_data:
                return Validation(
                    "To define a profile you must select an index or column name"
                )
            if "column" in form_data and "index" in form_data:
                return Validation(
                    "You must select an index value (to select a table "
                    "row) or a column name (to select a table column). You cannot "
                    "select both at the same time",
                )

        return Validation()

    def filter(self, form_data):
        """
        Remove fields depending on the value set in source.
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
            # convert form dict to list
            form_data["values"] = form_data["values"]["values"]

        self.logger.debug(f"Deleting keys: {keys_to_delete}")
        for key in keys_to_delete:
            form_data.pop(key, None)
