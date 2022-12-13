from pywr_editor.form import AbstractStringComboBoxWidget, FormField

"""
 Defines a widget to set the aggregation function
 used to aggregate parameters.
"""


class ParameterAggFuncWidget(AbstractStringComboBoxWidget):
    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected value.
        :param parent: The parent widget.
        """
        funcs = [
            "sum",
            "product",
            "min",
            "max",
            "mean",
            "median",
        ]
        labels_map = {}
        for fun in funcs:
            labels_map[fun] = fun.capitalize()

        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=labels_map,
            # the parameter does not have a default value. This is set below
            # because it is mandatory and is always returned
            keep_default=True,
            default_value="sum",
        )
