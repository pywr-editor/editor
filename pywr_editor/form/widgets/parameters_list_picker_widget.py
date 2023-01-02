from pywr_editor.form import AbstractParametersListPickerWidget, FormField


class ParametersListPickerWidget(AbstractParametersListPickerWidget):
    """
    Widget that provides a list of parameters.
    """

    def __init__(
        self,
        name: str,
        value: list[int | float | str | dict] | None,
        parent: FormField,
        is_mandatory: bool = True,
        include_param_key: list[str] | None = None,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The list of parameters or numbers.
        :param is_mandatory: Whether at least one parameter should be provided or the
        field can be left empty. Default to True.
        :param include_param_key: A string or list of strings representing parameter
        keys to only include in the widget. An error will be shown if any other
        parameter types is present in the value. The picker dialog will filter the
        parameter types as well.
        :param parent: The parent widget.
        """
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            is_mandatory=is_mandatory,
            include_param_key=include_param_key,
        )
