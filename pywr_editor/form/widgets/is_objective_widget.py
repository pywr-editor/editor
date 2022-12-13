from pywr_editor.form import FormField, AbstractStringComboBoxWidget

"""
 Defines a widget to set the objective on a recorder.
"""


class IsObjectiveWidget(AbstractStringComboBoxWidget):
    not_selected_str = "None"

    def __init__(self, name: str, value: str | None, parent: FormField):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected value.
        :param parent: The parent widget.
        """
        labels_map = {
            self.not_selected_str: "Disabled",
            "maximise": "Maximise",
            "minimise": "Minimise",
        }

        # check spelling
        if value in ["maximize", "max"]:
            value = "maximise"
        elif value in ["minimize", "min"]:
            value = "minimise"
        elif value is None:
            value = self.not_selected_str

        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=labels_map,
            default_value=self.not_selected_str,
        )
