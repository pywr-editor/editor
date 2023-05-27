from pywr_editor.form import AbstractStringComboBoxWidget, FormField

"""
 This widget handles the "kind" argument when the recorder "agg_func" or
 "temporal_agg_func" keys are set to "percentileofscore" during an
 optimisation or for numpy recorders respectively.
"""


class AggFuncPercentileOfScoreKindWidget(AbstractStringComboBoxWidget):
    def __init__(
        self,
        name: str,
        value: dict | None,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The dictionary from the "agg_func" or "temporal_agg_func" key.
        :param parent: The parent widget.
        """
        labels_map = {
            "rank": "Rank",
            "weak": "Weak",
            "strict": "Strict",
            "mean": "Mean",
        }

        _value = None
        # the method is stored in the "kwargs" key
        if isinstance(value, dict) and "kwargs" in value and "kind" in value["kwargs"]:
            _value = value["kwargs"]["kind"]

        super().__init__(
            name=name,
            value=_value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=labels_map,
            default_value=self.get_default_value(),
        )

    def get_default_value(self) -> str:
        """
        Returns the default value.
        :return: The default method.
        """
        return "rank"
