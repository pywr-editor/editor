from pywr_editor.form import AbstractStringComboBoxWidget, FormField
from pywr_editor.utils import Logging

"""
 Defines a widget to set the relation symbol used in the
 predicate for a threshold parameter.
"""


class ThresholdRelationSymbolWidget(AbstractStringComboBoxWidget):
    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected parameter name.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)

        # replace symbol with string
        if value == "<":
            value = "LT"
        elif value == ">":
            value = "GT"
        elif value == "=":
            value = "EQ"
        elif value == "<=":
            value = "LE"
        elif value == ">=":
            value = "GE"

        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map={
                "LT": "Less (<)",
                "GT": "Greater (>)",
                "EQ": "Equal (=)",
                "LE": "Less or equal (<=)",
                "GE": "Greater or equal (<=)",
            },
            # the parameter does not have a default value. This is set below
            # because it is mandatory and is always returned
            keep_default=True,
            default_value="LT",
        )
