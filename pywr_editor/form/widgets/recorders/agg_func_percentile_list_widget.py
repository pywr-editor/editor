from pywr_editor.form import AbstractFloatListWidget, FormField, FormValidation

"""
 This widgets handles the percentile or list of percentiles to use
 when "agg_func" (for optimisations) or "temporal_agg_func" (for numpy
 recorders) is set to "percentile".

 See: https://numpy.org/doc/stable/reference/generated/numpy.percentile.html
"""


class AggFuncPercentileListWidget(AbstractFloatListWidget):
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

        _value = None
        # list is stored in the "args" key
        if isinstance(value, dict) and "args" in value:
            _value = value["args"]

        super().__init__(
            name=name,
            value=_value,
            allowed_item_types=(float, int),
            only_list=False,
            final_type=float,
            # list of percentiles is an arg parameter and is mandatory
            allowed_empty=False,
            log_name=self.__class__.__name__,
            parent=parent,
        )

    def validate(
        self, name: str, label: str, value: int | float | list[int | float]
    ) -> FormValidation:
        """
        Checks that the percentiles are between 0 and 100.
        :param name: The field name.
        :param label: The field label.
        :param value: The field label.
        :return: The FormValidation instance.
        """
        status = super().validate(name, label, value)

        # if there is already an error, return parent result
        if not status.validation:
            return status

        # check that all numbers are between 0 and 100
        if isinstance(value, (int, float)) and not (0 <= value <= 100):
            return FormValidation(
                error_message="The percentile must be a number between 0 and 100",
                validation=False,
            )
        elif isinstance(value, list) and not all(
            [0 <= p <= 100 for p in value]
        ):
            return FormValidation(
                error_message="The percentiles must be numbers between 0 and 100",
                validation=False,
            )

        return FormValidation(validation=True)
