from pywr_editor.form import FormField, AbstractModelComponentLineEditWidget

"""
 This widget displays a non-editable QLineEdit and
 buttons that allow selecting and existing recorder
 or defining a new one via a dialog.
"""


class RecorderLineEditWidget(AbstractModelComponentLineEditWidget):
    def __init__(
        self,
        name: str,
        value: str | dict,
        parent: FormField,
        is_mandatory: bool = True,
        include_recorder_key: list[str] | None = None,
    ):
        """
        Initialises the widget to select a recorder. The recorder can be a string,
        when it refers to a model recorder, a dictionary, for anonymous recorders
        loaded via the "url" or "table" keys, or a number, for a constant recorder.
        :param name: The field name.
        :param value: The recorder value.
        :param parent: The parent widget.
        :param is_mandatory: Whether the recorder must be provided or the field can
        be left empty. Default to True.
        :param include_recorder_key: A string or list of strings representing recorder
        keys to only include in the widget. An error will be shown if the recorder
        type provided as value is not allowed. The picker dialog will also filter
        the recorder types.
        """
        super().__init__(
            name=name,
            value=value,
            parent=parent,
            component_type="recorder",
            is_mandatory=is_mandatory,
            include_comp_key=include_recorder_key,
        )
