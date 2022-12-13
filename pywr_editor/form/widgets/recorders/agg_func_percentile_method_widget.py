from pywr_editor.form import AbstractStringComboBoxWidget, FormField

"""
 This widget handles the "method" argument when the recorder aggregation
 function is set to "percentile" during an optimisation or for numpy
 recorders. The Default method is set to "linear".
"""


class AggFuncPercentileMethodWidget(AbstractStringComboBoxWidget):
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
            # from https://numpy.org/doc/stable/reference/generated/numpy.percentile.html # noqa: E501
            "inverted_cdf": "Inverted CDF",
            "averaged_inverted_cdf": "Averaged inverted CDF",
            "closest_observation": "Closest observation",
            "interpolated_inverted_cdf": "Interpolated inverted CDF",
            "hazen": "Hazen",
            "weibull": "Weibull",
            "linear": "Linear",
            "median_unbiased": "Median unbiased",
            "normal_unbiased": "Normal unbiased",
            "lower": "Lower",
            "higher": "Higher",
            "midpoint": "Midpoint",
            "nearest": "Nearest",
        }

        _value = None
        # the method is stored in the "kwargs" key
        if (
            isinstance(value, dict)
            and "kwargs" in value
            and "method" in value["kwargs"]
        ):
            _value = value["kwargs"]["method"]

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
        return "linear"
