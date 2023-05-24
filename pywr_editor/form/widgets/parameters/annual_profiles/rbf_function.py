from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import FormCustomWidget, FormField
from pywr_editor.utils import Logging
from pywr_editor.widgets import ComboBox


class RbfFunction(FormCustomWidget):
    value_map: dict[str, str] = {
        "multiquadric": "Multi-quadric",
        "inverse": "Inverse",
        "gaussian": "Gaussian",
        "linear": "Linear",
        "cubic": "Cubic",
        "quintic": "Quintic",
        "thin_plate": "Thin plate",
    }

    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
    ):
        """
        Initialises the widget to handle the "function" key of a radial basis profile
        parameter.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")
        self.warning_message = None

        super().__init__(name, value, parent)

        # add widgets
        self.value, self.warning_message = self.sanitise_value(value)
        self.combo_box = ComboBox()
        self.combo_box.setObjectName(f"{name}_combo_box")
        self.combo_box.addItems(list(self.value_map.values()))

        # set layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)

        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        self.combo_box.setCurrentText(self.value)
        self.field.set_warning(self.warning_message)

    def sanitise_value(self, value: str | None) -> [str | None, str | None]:
        """
        Sanitises the value.
        :param value: The value to sanitise.
        :return: The sanitised value and the warning message.
        """
        self.logger.debug(f"Sanitising value '{value}'")
        message = None

        # value is optional
        if value is None:
            self.logger.debug("Value is None. Returning default value")
            return self.get_default_value(), None

        # value is not a string
        if isinstance(value, str) is False:
            message = "The value set in the model configuration is not a valid type"
        elif value.lower() not in list(self.value_map.keys()):
            message = (
                "The value set in the model configuration is not valid. "
                + "Using default value"
            )

        # return None if the values are incorrect
        if message is not None:
            self.logger.debug(
                message + ". Returning default value with warning message"
            )
            return self.get_default_value(), message
        else:
            return self.value_map[value.lower()], message

    def get_value(self) -> str | None:
        """
        Returns the value.
        :return: The set value in the ComboBox.
        """
        value = self.combo_box.currentText()

        # return the proper key
        all_keys = list(self.value_map.keys())
        all_values = list(self.value_map.values())
        return all_keys[all_values.index(value)]

    def get_default_value(self) -> str:
        """
        The field default value.
        :return: Returns None.
        """
        return "multiquadric"

    def reset(self) -> None:
        """
        Resets the widget. This sets the ComboBox's value to "None".
        :return: None
        """
        self.combo_box.setCurrentText(self.value_map[self.get_default_value()])
