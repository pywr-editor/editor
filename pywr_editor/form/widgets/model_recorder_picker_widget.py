from pywr_editor.form import AbstractStringModelComponentPickerWidget, FormField

"""
 This widgets displays a list of available model recorders
 and allows the user to pick one.
"""


class ModelRecorderPickerWidget(AbstractStringModelComponentPickerWidget):
    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
        include_recorder_key: list[str] | None = None,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected recorder name.
        :param parent: The parent widget.
        :param include_recorder_key: A list of strings representing parameter keys to
        only include in the widget. An error will be shown if a not allowed parameter
        type is used as value.
        """
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            component_type="recorder",
            include_comp_key=include_recorder_key,
        )
