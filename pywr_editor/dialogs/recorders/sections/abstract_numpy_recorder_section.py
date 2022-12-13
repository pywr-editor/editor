from dataclasses import dataclass
from ..recorder_dialog_form import RecorderDialogForm
from .abstract_recorder_section import AbstractRecorderSection
from pywr_editor.form import (
    AggFuncPercentileMethodWidget,
    AggFuncPercentileOfScoreScoreWidget,
    AggFuncPercentileOfScoreKindWidget,
    AggFuncPercentileListWidget,
    TemporalAggFuncWidget,
    validate_percentile_field_section,
    AbstractAggFuncWidget,
)


"""
 Handles the label and description of the "temporal_agg_func"
 FormField.
"""


@dataclass
class TemporalWidgetField:
    label: str | None = None
    """ The label for the "temporal_agg_func" FormField. """
    help_text: str | None = None
    """ The description for the "temporal_agg_func" FormField. """

    def __post_init__(self):
        """
        Initialises the fields.
        """
        if self.label is None:
            self.label = "Temporal aggregation function"
        if self.help_text is None:
            self.help_text = "Function to use to temporally aggregate values "
            self.help_text += "from each scenario"


"""
 Defines a generic section for a numpy recorder to handle the
 temporal_agg_func_key. This inherits from AbstractRecorderSection
 to includes the optimisation fields as well.
"""


class AbstractNumpyRecorderSection(AbstractRecorderSection):
    def __init__(
        self,
        form: RecorderDialogForm,
        section_data: dict,
        section_fields: list[dict],
        log_name: str,
        agg_func_field_labels: TemporalWidgetField = TemporalWidgetField(),
        show_ignore_nan_field: bool = False,
        additional_sections: dict[str, list[dict]] | None = None,
    ):
        """
        Initialises the form section for a numpy recorder.
        :param form: The parent form.
        :param section_data: A dictionary containing data to pass to the widget.
        :param section_fields: A list containing the fields to add to the
        section.
        :param log_name: The name of the log.
        :param agg_func_field_labels: An instance of TemporalWidgetField to customise
        the label and help_text of the "temporal_agg_func" FormField.
        :param show_ignore_nan_field: Shows the "ignore_nan" field. The field used by
        some recorders inc combination with "temporal_gg_func". This is used by the
        values() method aof a recorder and it is passed to the Aggregator class
        with temporal_gg_func.
        :param additional_sections: Additional lists of sections to add to the
        section. This is must be a dictionary with the section title as key
        and list of fields as values. The sections will be added after the
        "Configuration" section but before the "Optimisation" section.
        """
        super().__init__(
            form=form,
            section_data=section_data,
            section_fields=section_fields,
            additional_sections=additional_sections,
            log_name=log_name,
        )

        # append section fields to handle the temporal_agg_func key
        self.section_fields += [
            {
                "name": "temporal_agg_func",
                "label": agg_func_field_labels.label,
                "value": self.form.get_recorder_dict_value("temporal_agg_func"),
                "field_type": TemporalAggFuncWidget,
                "help_text": agg_func_field_labels.help_text,
            },
            # fields when temporal_agg_func is "percentile"
            {
                "name": TemporalAggFuncWidget.agg_func_percentile_method,
                "label": "Percentile method",
                "value": self.form.get_recorder_dict_value("temporal_agg_func"),
                "field_type": AggFuncPercentileMethodWidget,
                "help_text": "Method to use for estimating the percentile. "
                + "When empty, it defaults to 'Linear'",
            },
            {
                "name": TemporalAggFuncWidget.agg_func_percentile_list,
                "label": "List of percentiles",
                "value": self.form.get_recorder_dict_value("temporal_agg_func"),
                "field_type": AggFuncPercentileListWidget,
                "validate_fun": validate_percentile_field_section,
                "help_text": "Percentile or comma-separated list of percentiles to "
                + "compute, which must be between 0 and 100 inclusive",
            },
            # fields when temporal_agg_func is "percentileofscore"
            {
                "name": TemporalAggFuncWidget.agg_func_percentileofscore_score,
                "label": "Score",
                "value": self.form.get_recorder_dict_value("temporal_agg_func"),
                "field_type": AggFuncPercentileOfScoreScoreWidget,
                "help_text": "Score to compute percentiles for",
            },
            {
                "name": TemporalAggFuncWidget.agg_func_percentileofscore_kind,
                "label": "Kind",
                "value": self.form.get_recorder_dict_value("temporal_agg_func"),
                "field_type": AggFuncPercentileOfScoreKindWidget,
                "help_text": "The method to use to compute the percentile rank. "
                + "When empty, it defaults to 'Rank'",
            },
        ]

        if show_ignore_nan_field:
            self.section_fields.append(
                {
                    "name": "ignore_nan",
                    "value": self.form.get_recorder_dict_value("ignore_nan"),
                    "field_type": "boolean",
                    "default_value": False,
                    "help_text": "Ignore NaNs in the recorder values when the "
                    + "optimiser aggregates the values from each scenario",
                }
            )

    def filter(self, form_data):
        """
        Groups the optimisation fields for the "temporal_agg_func" field.
        :param form_data: The form dictionary,
        :return: None
        """
        # call filter from parent section
        super().filter(form_data)

        # handle "temporal_agg_func" field
        func_widget: AbstractAggFuncWidget = self.form.find_field_by_name(
            "temporal_agg_func"
        ).widget
        func_widget.merge_form_dict_fields(form_data)
