from PySide6.QtWidgets import QVBoxLayout

from pywr_editor.form import FormCustomWidget, FormField
from pywr_editor.utils import Logging
from pywr_editor.widgets import ComboBox

"""
  Provides a ComboBox with a list of strings to
  choose from.
"""


class AbstractStringComboBoxWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
        log_name: str,
        labels_map: dict[str, str],
        default_value: str,
        keep_default: bool = False,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected parameter name.
        :param parent: The parent widget.
        :param log_name: The name of the logger.
        :param labels_map: A dictionary containing the values as keys and their labels
        as values.
        :param default_value: The default string to select when no value or a wrong
        value is provided.
        :param keep_default: If False, the widget returns None if the default value is
        selected. Default to False.
        """
        self.logger = Logging().logger(log_name)
        self.logger.debug(f"Loading widget with value {value}")
        super().__init__(name, value, parent)

        self.labels_map = labels_map
        self.default_value = default_value
        self.keep_default = keep_default

        self.label, self.warning_message = self.sanitise_value(value)

        # add the ComboBox
        self.combo_box = ComboBox()
        # sort values alphabetically
        items = sorted((list(self.labels_map.values())))
        # move None on top if present
        if "None" in items:
            items.insert(0, items.pop(items.index("None")))

        self.combo_box.addItems(items)
        self.combo_box.setCurrentText(self.label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

        # post-render actions
        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        self.form_field.set_warning_message(self.warning_message)

    def sanitise_value(self, value: str | None) -> [str, str | None]:
        """
        Sanitises the field value.
        :param value: The value to sanitise.
        :return: The label and the warning message.
        """
        # check if str, and in list
        self.logger.debug(f"Sanitising value {value}")
        message = None

        label = self.labels_map[self.get_default_selection()]
        # user-provided value may have a wrong case. Ensure correct matching
        lower_case_map = {key.lower(): label for key, label in self.labels_map.items()}

        # check value
        if value is None:
            self.logger.debug("The value is not provided. Using default.")
        elif not isinstance(value, str) or value == "":
            message = (
                "The value provided in the model configuration is not a " + "valid type"
            )
            self.logger.debug(message)
        elif isinstance(value, str) and value.lower() not in lower_case_map:
            message = "The value provided in the model configuration does not exist"
            self.logger.debug(message)
        else:
            # user-provided value may have a wrong case
            label = lower_case_map[value.lower()]
        return label, message

    def get_default_selection(self) -> str:
        """
        The string to select when no value is provided.
        :return: The default selection.
        """
        return self.default_value

    def get_value(self) -> str | None:
        """
        Returns the value from the label.
        :return: The value as string.
        """
        current_label = self.combo_box.currentText()
        all_labels = list(self.labels_map.values())
        all_values = list(self.labels_map.keys())

        index = all_labels.index(current_label)
        if all_values[index] == self.default_value and self.keep_default is False:
            return None
        return all_values[index]

    def reset(self) -> None:
        """
        Resets the widget by setting the default value.
        """
        self.combo_box.setCurrentText(self.labels_map[self.get_default_selection()])
