from pywr_editor.form import AbstractModelComponentsListPickerWidget, FormField

"""
 Widgets that provides a list of parameters.
"""


class AbstractParametersListPickerWidget(
    AbstractModelComponentsListPickerWidget
):
    def __init__(
        self,
        name: str,
        value: list[int | float | str | dict] | None,
        parent: FormField,
        log_name: str,
        is_mandatory: bool = True,
        show_row_numbers: bool = False,
        row_number_label: str | None = None,
        include_param_key: list[str] | None = None,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The list of parameters or numbers.
        :param parent: The parent widget.
        :param log_name: The name to use in the logger.
        :param is_mandatory: Whether at least one parameter should be provided or the
        field can be left empty. Default to True.
        :param show_row_numbers: Shows the number of the row in the table. Default to
        False.
        :param row_number_label: The column label for the row numbers.
        :param include_param_key: A string or list of strings representing parameter
        keys to only include in the widget. An error will be shown if any other
        parameter types is present in the value. The picker dialog will filter the
        parameter types as well.
        """
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            component_type="parameter",
            log_name=log_name,
            is_mandatory=is_mandatory,
            show_row_numbers=show_row_numbers,
            row_number_label=row_number_label,
            include_component_key=include_param_key,
        ),
