from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import FormCustomWidget, FormField
from pywr_editor.utils import Logging
from pywr_editor.widgets import CheckableComboBox

"""
 This widgets displays a list of available model parameters
 and allows the user to select multiple ones.
"""


class MultiParameterPickerWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: list[str] | None,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected parameter names.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")
        super().__init__(name, value, parent)

        self.model_config = self.form.model_config

        # add parameter names
        self.combo_box = CheckableComboBox()
        model_parameters = self.model_config.parameters.names
        for name in model_parameters:
            param_obj = self.model_config.parameters.config(
                parameter_name=name, as_dict=False
            )
            self.combo_box.addItem(f"{name} ({param_obj.humanised_type})", name)

        # set selected
        if not value:
            self.logger.debug("Value is None or empty. No value set")
        # value must be a list of strings
        elif not isinstance(value, list):
            message = "The parameter names must be a list"
            self.form_field.set_warning_message(message)
            self.logger.debug(message + ". None selected")
        elif not all([isinstance(n, str) for n in value]):
            message = "The parameter names must be valid strings"
            self.form_field.set_warning_message(message)
            self.logger.debug(message + ". None selected")
        else:
            wrong_names = []
            selected_indexes = []
            # check that names exists
            for param_name in value:
                index = self.combo_box.findData(param_name, Qt.UserRole)
                if index != -1:
                    self.logger.debug(f"Selecting index #{index} for '{param_name}'")
                    selected_indexes.append(index)
                else:
                    wrong_names.append(param_name)
            # select valid names
            self.combo_box.check_items(selected_indexes, False)

            if wrong_names:
                message = (
                    "The following parameter names do not exist in the model "
                    + f"configuration: {', '.join(wrong_names)}"
                )
                self.logger.debug(message)
                self.form_field.set_warning_message(message)

        # there are no parameters in the model
        if len(self.combo_box.all_items) == 0:
            self.combo_box.setEnabled(False)
            message = "There are no parameters available"
            self.logger.debug(message)
            self.form_field.set_warning_message(
                message + ". Add a new parameter first, before setting up this option"
            )

        # layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

    def get_value(self) -> list[str]:
        """
        Returns the selected parameter names.
        :return: The names, None if nothing is selected
        """
        return self.combo_box.checked_items(use_data=True)

    def reset(self) -> None:
        """
        Reset the widget by selecting no parameter.
        :return: None
        """
        self.combo_box.uncheck_all()
