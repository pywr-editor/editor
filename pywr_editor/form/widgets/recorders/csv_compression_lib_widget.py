from pywr_editor.form import AbstractStringComboBoxWidget, FormField

"""
 Defines a widget to select the compression algorithm for
 the CSV recorder.
"""


class CSVCompressionLibWidget(AbstractStringComboBoxWidget):
    default_value_str = "None"

    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected method.
        :param parent: The parent widget.
        """
        if value and value == "bz2":
            value = "bzip2"
        labels_map = {
            self.default_value_str: "Disabled",
            "gzip": "GZIP",
            "bzip2": "BZIP2",
        }

        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=labels_map,
            default_value=self.default_value_str,
        )
