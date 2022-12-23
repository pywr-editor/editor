from pywr_editor.form import AbstractModelNodePickerWidget, FormField

"""
 This widgets displays a list of available model nodes
 and allows the user to pick one.

 All the nodes inherits from AbstractNode in pywr.
"""


class NodePickerWidget(AbstractModelNodePickerWidget):
    def __init__(
        self, name: str, value: str | None, parent: FormField, is_mandatory=True
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected node name.
        :param parent: The parent widget.
        :param is_mandatory: Whether the field must be provided or can be left empty.
        Default to True.
        """
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            is_mandatory=is_mandatory,
        )
