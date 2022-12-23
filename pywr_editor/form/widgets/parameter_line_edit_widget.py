from pywr_editor.form import AbstractModelComponentLineEditWidget, FormField

"""
 This widget displays a non-editable QLineEdit and
 buttons that allow selecting and existing parameter
 or defining a new one via a dialog.
"""


class ParameterLineEditWidget(AbstractModelComponentLineEditWidget):
    def __init__(
        self,
        name: str,
        value: str | dict | int | float,
        parent: FormField,
        is_mandatory: bool = True,
        include_param_key: list[str] | None = None,
    ):
        """
        Initialises the widget to select a parameter. The parameter can be a string,
        when it refers to a model parameter, a dictionary, for anonymous parameters
        loaded via the "url" or "table" keys, or a number, for a constant parameter.
        :param name: The field name.
        :param value: The parameter value.
        :param parent: The parent widget.
        :param is_mandatory: Whether the parameter must be provided or the field can
        be left empty. Default to True.
        :param include_param_key: A string or list of strings representing parameter
        keys to only include in the widget. An error will be shown if the parameter
        type provided as value is not allowed. The picker dialog will also filter
        the parameter types.
        """
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            component_type="parameter",
            is_mandatory=is_mandatory,
            include_comp_key=include_param_key,
        )
