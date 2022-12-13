from pywr_editor.form import FormField, AbstractParametersListPickerWidget

"""
 Widget that provides a list of parameters.
"""


class ParametersListPickerWidget(AbstractParametersListPickerWidget):
    def __init__(
        self,
        name: str,
        value: list[int | float | str | dict] | None,
        parent: FormField,
        is_mandatory: bool = True,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The list of parameters or numbers.
        :param is_mandatory: Whether at least one parameter should be provided or the
        field can be left empty. Default to True.
        :param parent: The parent widget.
        """
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            is_mandatory=is_mandatory,
        )
