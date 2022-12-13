from pywr_editor.form import AbstractStringComboBoxWidget, FormField

"""
 Defines a widget to select the resampling frequency
 of a DataFrame.
"""


class ResampleAggFrequencyWidget(AbstractStringComboBoxWidget):
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
        # rename strings when Pandas offers more than one value to define the frequency
        if isinstance(value, str):
            value_u = value.upper()
            # year end frequency
            if value_u == "A":
                value = "Y"
            # business year end frequency
            elif value_u == "BA":
                value = "BY"
            # year start frequency
            elif value_u == "AS":
                value = "YS"
            # business year start frequency
            elif value_u == "BAS":
                value = "BYS"

        # from https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases # noqa: E501
        # some frequencies are omitted
        labels_map = {
            self.default_value_str: "Disabled",
            "B": "Business day frequency",
            "D": "Calendar day",
            "W": "Weekly",
            "M": "Month end",
            "SM": "Semi-month end (15th and end of month)",
            "BM": "Business month end",
            "MS": "Month start",
            "SMS": "Semi-month start (1st and 15th)",
            "BMS": "Business month start",
            "Q": "Quarter end",
            "BQ": "Business quarter end",
            "QS": "Quarter start",
            "BQS": "Business quarter start",
            "Y": "Year end",
            "BY": "Business year end",
            "YS": "Year start",
            "BYS": "Business year start",
        }

        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=labels_map,
            default_value=self.default_value_str,
        )
