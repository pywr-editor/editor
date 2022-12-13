from pywr_editor.form import FormField, ModelComponentTypeSelectorWidget
from pywr_editor.model import ParameterConfig

"""
 ComboBox that shows a list of parameter types. This
 includes all pywr built-in parameters and custom
 parameters declared in the JSON "includes" field.
"""


class ParameterTypeSelectorWidget(ModelComponentTypeSelectorWidget):
    def __init__(
        self,
        name: str,
        value: ParameterConfig,
        parent: FormField,
        include_param_key: list[str] = None,
    ):
        """
        Initialises the widget to select the parameter type.
        :param name: The field name.
        :param value: The ParameterConfig instance of the selected parameter.
        :param parent: The parent widget.
        :param include_param_key: A list of strings representing parameter keys to only
        include in the widget. An error will be shown if a not allowed parameter type
        is used as value.
        """
        super().__init__(
            component_type="parameter",
            name=name,
            value=value,
            parent=parent,
            include_comp_key=include_param_key,
            log_name=self.__class__.__name__,
        )
