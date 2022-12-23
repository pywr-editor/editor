from pywr_editor.form import FloatWidget, FormField, FormValidation

"""
 This widget handles the "score" argument when the recorder "agg_func" or
 "temporal_agg_func" keys are set to "percentileofscore" during an
 optimisation or for numpy recorders respectively.
"""


class AggFuncPercentileOfScoreScoreWidget(FloatWidget):
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
        # the method is stored in the "kwargs" key
        if (
            isinstance(value, dict)
            and "kwargs" in value
            and "score" in value["kwargs"]
        ):
            _value = value["kwargs"]["score"]

        super().__init__(
            name=name,
            value=_value,
            parent=parent,
        )

    def validate(self, name, label, value):
        """
        Checks that the score is provided.
        :param name: The field name.
        :param label: The field label.
        :param value: The field label. This is not used.
        :return: The FormValidation instance.
        """
        status = super().validate(name, label, value)

        if not status.validation:
            return status

        if not value:
            return FormValidation(
                error_message="You must provide a value",
                validation=False,
            )
        return FormValidation(validation=True)
