from pywr_editor.form import AbstractStringComboBoxWidget, FormField

"""
 Defines a widget to set the aggregation functions
 used to aggregated the tracked parameter values
 for each scenario (A) and to aggregated then A
 for all scenarios with a different function in
 the EventStatisticRecorder.
"""


class EventStatisticAggFuncWidget(AbstractStringComboBoxWidget):
    def __init__(
        self,
        name: str,
        value: dict[str, str | None],
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: A dictionary containing the "recorder_agg_func" or
        "event_agg_func" and "agg_func" keys.
        :param parent: The parent widget.
        """
        labels_map = {
            "mean": "Mean",
            "sum": "Sum",
            "size": "Group size (include NaN)",
            "count": "Group size (exclude NaN)",
            "std": "Standard deviation",
            "var": "Variance",
            "sem": "Standard error of the mean",
            "first": "First value",
            "last": "Last value",
            "min": "Minimum",
            "max": "Maximum",
        }
        # the field key to use to fetch the values ("recorder_agg_func" or
        # "event_agg_func")
        key = parent.name

        selected_value = None
        # function is provided
        if value[key] is not None:
            selected_value = value[key]
        # function is not provided, field defaults to value provided
        # in "agg_func" key, if it is defined
        elif value["agg_func"] is not None:
            selected_value = value["agg_func"]

        super().__init__(
            name=name,
            value=selected_value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=labels_map,
            # widget defaults to "agg_func" or "mean" when
            # "agg_func" is None
            default_value="mean",
        )
