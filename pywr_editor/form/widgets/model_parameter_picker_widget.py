from pywr_editor.form import AbstractStringModelComponentPickerWidget, FormField

"""
 This widgets displays a list of available model parameters
 and allows the user to pick one.

 Parameter types can also be filtered to show only
 the allowed ones.
"""


class ModelParameterPickerWidget(AbstractStringModelComponentPickerWidget):
    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
        include_param_key: list[str] | None = None,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected parameter name.
        :param parent: The parent widget.
        :param include_param_key: A list of strings representing parameter keys to only
        include in the widget. An error will be shown if a not allowed parameter type
        is used as value.
        """
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            component_type="parameter",
            include_comp_key=include_param_key,
        )
