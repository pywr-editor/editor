from pywr_editor.form import FormField, AbstractStringComboBoxWidget

"""
 This widget handles the mode strings to open a file.
 This is used for a TablesRecorder
"""


class FileModeWidget(AbstractStringComboBoxWidget):
    def __init__(self, name: str, value: dict | None, parent: FormField):
        """
        Initialises the widget.
        :param name: The name,
        :param value: A selected file mode.
        :param parent: The parent widget.
        """
        # ignore readonly
        labels_map = {
            "w": "w -  overwrite existing file with same name",
            "a": "a - Append to existing file; create file if missing",
            "r+": "r+ - Append to existing file; raise error if file is missing",
        }

        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=labels_map,
            default_value="w",
        )
