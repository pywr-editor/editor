from pywr_editor.form import AbstractStringComboBoxWidget, FormField

"""
 Defines a widget to set the interpolation method.
"""


class InterpKindWidget(AbstractStringComboBoxWidget):
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
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map={
                "linear": "Linear",
                "nearest": "Nearest (round down half-integers)",
                "nearest-up": "Nearest up (round up half-integers)",
                "zero": "Spline of zeroth order",
                "slinear": "Spline of first order",
                "quadratic": "Spline of second order",
                "cubic": "Spline of third order",
                "previous": "Previous value of the point",
                "next": "Next value of the point",
            },
            default_value="linear",
        )
