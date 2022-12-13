from pywr_editor.form import AbstractStringComboBoxWidget, FormField

"""
 Defines a widget to select the aggregation function
 of a DataFrame.
"""


class ResampleAggFunctionWidget(AbstractStringComboBoxWidget):
    default_value_str = "None"

    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected frequency.
        :param parent: The parent widget.
        """
        labels_map = {
            self.default_value_str: "Disabled",
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

        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=labels_map,
            default_value=self.default_value_str,
        )
