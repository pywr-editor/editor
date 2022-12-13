from pywr_editor.form import AbstractStringComboBoxWidget, FormField

"""
 Defines a widget to set the aggregation function
 used to aggregate recorders.
"""


class RecorderAggFuncWidget(AbstractStringComboBoxWidget):
    def __init__(
        self,
        name: str,
        value: dict[str, str | None],
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: A dictionary containing the "recorder_agg_func" and "agg_func"
        keys with the selected values for the recorder aggregation and scenario
        aggregation.
        :param parent: The parent widget.
        """
        labels_map = {}
        for fun in [
            "sum",
            "product",
            "min",
            "max",
            "mean",
        ]:
            labels_map[fun] = fun.capitalize()

        selected_value = None
        # function is provided
        if value["recorder_agg_func"] is not None:
            selected_value = value["recorder_agg_func"]
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
            # field is mandatory and does not have a default value. It defaults
            # to agg_func in Pywr but the key may be None
            keep_default=True,
            # key does not have a default value in Pywr, this is forced to
            # mean because the value is mandatory
            default_value="mean",
        )
