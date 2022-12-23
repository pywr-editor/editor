from pywr_editor.form import AbstractRecordersListPickerWidget, FormField

"""
 Widgets that provides a list of recorders.
"""


class RecordersListPickerWidget(AbstractRecordersListPickerWidget):
    def __init__(
        self,
        name: str,
        value: list[str | dict] | None,
        parent: FormField,
        is_mandatory: bool = True,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The list of recorders.
        :param parent: The parent widget.
        :param is_mandatory: Whether at least one recorder should be provided or the
        field can be left empty. Default to True.
        """
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            is_mandatory=is_mandatory,
        )
