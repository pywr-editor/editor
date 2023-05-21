from typing import Any

from PySide6.QtWidgets import QMessageBox, QPushButton, QWidget

from pywr_editor.form import (
    AggFuncPercentileListWidget,
    AggFuncPercentileMethodWidget,
    AggFuncPercentileOfScoreKindWidget,
    AggFuncPercentileOfScoreScoreWidget,
    FloatWidget,
    FormValidation,
    IsObjectiveWidget,
    ModelComponentForm,
    OptAggFuncWidget,
    validate_percentile_field_section,
)
from pywr_editor.model import ModelConfig, RecorderConfig
from pywr_editor.utils import Logging

"""
 This widgets define a base class of a form that change a recorder
 configuration.

 This class does not render any field. The form can be validated
 and its configuration can be returned by calling the self.save()
 method.
"""


class RecorderForm(ModelComponentForm):
    optimisation_config_group_name = "Optimisation"

    def __init__(
        self,
        model_config: ModelConfig,
        recorder_obj: RecorderConfig | None,
        available_fields: dict,
        save_button: QPushButton,
        parent: QWidget,
        enable_optimisation_section: bool = True,
    ):
        """
        Initialises the parameter form.
        :param model_config: The ModelConfig instance.
        :param recorder_obj: The RecorderConfig instance of the selected recorder.
        :param save_button: The button used to save the form.
        :param parent: The parent widget.
        :param enable_optimisation_section: If False the optimisation section of a
        recorder will not be shown. Default to True.
        """
        self.logger = Logging().logger(self.__class__.__name__)

        self.recorder_obj = recorder_obj
        if recorder_obj is not None:
            self.recorder_dict = recorder_obj.props
        else:
            self.recorder_dict = {}

        super().__init__(
            form_dict=self.recorder_dict,
            model_config=model_config,
            available_fields=available_fields,
            save_button=save_button,
            parent=parent,
        )

        # clean up dictionary if it contains mixed configurations
        # (for example for table and external file)
        self.clean_keys()
        self.section_form_data["recorder_obj"] = self.recorder_obj
        self.section_form_data[
            "enable_optimisation_section"
        ] = enable_optimisation_section
        self.recorders_data = self.model_config.pywr_recorder_data
        self.show_warning = False

    def load_fields(self) -> None:
        """
        Loads the fields.
        :return: None
        """
        if self.loaded is True:
            return

        if self.show_warning:
            QMessageBox.warning(
                self,
                "Mixed configuration",
                "The recorder configuration has been adjusted because it contained "
                "mixed configurations. This happens when you edited the model "
                "configuration file manually and you connected the recorder, for "
                "example, to a table and an external file at the same time.\n\n"
                "If the configuration is not what you expect, manually edit the model "
                "file and restart the editor. Pywr always uses this priority order for "
                "the dictionary keys: 'value', 'table' and 'url'",
                QMessageBox.StandardButton.Ok,
            )

        super().load_fields()

    def get_recorder_dict_value(self, key: str) -> Any:
        """
        Gets a value from the recorder configuration.
        :param key: The key to extract the value of.
        :return: The value or empty if the key is not set.
        """
        return super().get_form_dict_value(key)

    def clean_keys(self) -> None:
        """
        Cleans up the parameter dictionary if it contains mixed configurations (for
        example for table and external file) Pywr priority order is value -> table
        -> url.
        :return: None
        """
        keys = self.recorder_dict.keys()
        keys_to_del = []

        if "value" in keys or "values" in keys:
            keys_to_del = ["table", "url", "index_col", "parse_dates"]
        elif "table" in keys:
            keys_to_del = ["value", "values", "url", "index_col", "parse_dates"]
        elif "url" in keys:
            keys_to_del = ["value", "values", "table"]

        for key in keys_to_del:
            if key in keys:
                del self.recorder_dict[key]

                # show message only with url, table and value keys
                if key not in ["index_col", "parse_dates"]:
                    self.show_warning = True

    @property
    def optimisation_section(self) -> dict[str, list[str, dict]]:
        """
        Returns the section with the optimisation fields.
        :return: A dictionary with the section name and its fields if the
        optimisation section is enabled, otherwise an empty dictionary.
        """
        if self.section_form_data["enable_optimisation_section"] is False:
            return {}

        return {
            self.optimisation_config_group_name: [
                {
                    "name": "is_objective",
                    "label": "Objective type",
                    "value": self.get_form_dict_value("is_objective"),
                    "field_type": IsObjectiveWidget,
                    "help_text": "If set, the recorder will be used in an optimisation"
                    + " problem and will be minimised or maximised",
                },
                {
                    "name": "constraint_lower_bounds",
                    "label": "Lower bound",
                    "value": self.get_recorder_dict_value("constraint_lower_bounds"),
                    "field_type": FloatWidget,
                    "help_text": "If provided, the optimisation problem will be  "
                    "bounded below. Leave it empty not to constraint the recorder "
                    "value",
                    "validate_fun": self._check_constraint_bounds,
                },
                {
                    "name": "constraint_upper_bounds",
                    "label": "Upper bound",
                    "value": self.get_recorder_dict_value("constraint_upper_bounds"),
                    "field_type": FloatWidget,
                    "help_text": "If provided, the optimisation problem will be "
                    + "bounded above. Leave it empty not to constraint the recorder "
                    + "value",
                },
                {
                    "name": "epsilon",
                    "value": self.get_recorder_dict_value("epsilon"),
                    "field_type": FloatWidget,
                    "default_value": 1,
                    "help_text": "Epsilon distance that may be used by an optimisation "
                    + "library",
                },
                {
                    "name": "agg_func",
                    "label": "Scenario aggregation function",
                    "value": self.get_recorder_dict_value("agg_func"),
                    "field_type": OptAggFuncWidget,
                    "help_text": "Function to use to aggregate values from each "
                    + "scenario during optimisation",
                },
                # fields when agg_func is "percentile"
                {
                    "name": OptAggFuncWidget.agg_func_percentile_method,
                    "label": "Percentile method",
                    "value": self.get_recorder_dict_value("agg_func"),
                    "field_type": AggFuncPercentileMethodWidget,
                    "help_text": "Method to use for estimating the percentile. "
                    + "When empty, it defaults to 'Linear'",
                },
                {
                    "name": OptAggFuncWidget.agg_func_percentile_list,
                    "label": "List of percentiles",
                    "value": self.get_recorder_dict_value("agg_func"),
                    "field_type": AggFuncPercentileListWidget,
                    "validate_fun": validate_percentile_field_section,
                    "help_text": "Percentile or comma-separated list of percentiles to"
                    + " compute, which must be between 0 and 100 inclusive",
                },
                # fields when agg_func is "percentileofscore"
                {
                    "name": OptAggFuncWidget.agg_func_percentileofscore_score,
                    "label": "Score",
                    "value": self.get_recorder_dict_value("agg_func"),
                    "field_type": AggFuncPercentileOfScoreScoreWidget,
                    "help_text": "Score to compute percentiles for",
                },
                {
                    "name": OptAggFuncWidget.agg_func_percentileofscore_kind,
                    "label": "Kind",
                    "value": self.get_recorder_dict_value("agg_func"),
                    "field_type": AggFuncPercentileOfScoreKindWidget,
                    "help_text": "The method to use to compute the percentile rank. "
                    + "When empty, it defaults to 'Rank'",
                },
            ]
        }

    def _check_constraint_bounds(
        self, name: str, label: str, lower_bound: float
    ) -> FormValidation:
        """
        Checks that the lower bound is smaller than the upper bound.
        :param name: The field name.
        :param label: The field label.
        :param lower_bound: The field value for the lower bound.
        :return: The validation instance.
        """
        upper_bound = self.find_field_by_name("constraint_upper_bounds").value()
        if lower_bound and upper_bound and lower_bound > upper_bound:
            return FormValidation(
                validation=False,
                error_message="The lower bound must be smaller than the upper limit",
            )

        return FormValidation(validation=True)

    def save(self) -> dict | bool:
        """
        Groups the optimisation fields for the agg_func field.
        :return: None
        """
        form_data = super().save()

        if form_data is False:
            return False

        if self.section_form_data["enable_optimisation_section"] is True:
            func_field = self.find_field_by_name("agg_func")
            if func_field:
                func_field.widget.merge_form_dict_fields(form_data)

        return form_data
