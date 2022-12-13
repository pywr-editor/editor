from pywr_editor.form import AbstractStringComboBoxWidget, FormField

"""
 Defines a widget to select the CSV parser dialect for
 the CSV recorder.
"""


class CSVDialectWidget(AbstractStringComboBoxWidget):
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

        labels_map = {
            "excel": "Excel-generated CSV file",
            "excel-tab": "Excel-generated TAB-delimited file",
            "unix": "CSV file generated on UNIX",
        }

        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=labels_map,
            default_value="excel",
        )
