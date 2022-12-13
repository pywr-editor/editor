from pywr_editor.form import FormField, ModelComponentTypeSelectorWidget
from pywr_editor.model import RecorderConfig

"""
 ComboBox that shows a list of recorder types. This
 includes all pywr built-in recorders and custom
 recorder declared in the JSON "includes" field.
"""


class RecorderTypeSelectorWidget(ModelComponentTypeSelectorWidget):
    def __init__(
        self,
        name: str,
        value: RecorderConfig,
        parent: FormField,
        include_recorder_key: list[str] = None,
    ):
        """
        Initialises the widget to select the recorder type.
        :param name: The field name.
        :param value: The RecorderConfig instance of the selected recorder.
        :param parent: The parent widget.
        :param include_recorder_key: A list of strings representing recorder keys to
        only include in the widget. An error will be shown if a not allowed recorder
        type is used as value.
        """
        super().__init__(
            component_type="recorder",
            name=name,
            value=value,
            parent=parent,
            include_comp_key=include_recorder_key,
            log_name=self.__class__.__name__,
        )
