from typing import Any

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from pywr_editor.form import FormField, FormWidget
from pywr_editor.utils import Logging
from pywr_editor.widgets import DoubleSpinBox

"""
 Defines a widget to set and provide values when the
 predicate for a threshold parameter is false or
 true using QDoubleSpinBox widgets.
 NOTE: validation is not necessary as the QDoubleSpinBox
 always initialises with 0 if the values are not provided
 or when they are not correct.
"""


class ThresholdValuesWidget(FormWidget):
    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected parameter name.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget with value {value}")
        super().__init__(name, value, parent)

        self.value, self.warning_message = self.sanitise_value(value)

        # add layout and widget
        self.spin_boxes: list[DoubleSpinBox] = []
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for li, label in enumerate(["Predicate is false", "Predicate is true"]):
            field_layout = QVBoxLayout()
            field_label = QLabel(label)

            double_spin_box = DoubleSpinBox(parent=parent)
            # set value if available
            if self.value[li] is not None:
                double_spin_box.setValue(self.value[li])

            self.spin_boxes.append(double_spin_box)
            field_layout.addWidget(field_label)
            field_layout.addWidget(double_spin_box)
            layout.addLayout(field_layout)

        self.setLayout(layout)

        # post-render actions
        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        self.field.set_warning(self.warning_message)

    def sanitise_value(self, value: Any) -> [list, str | None]:
        """
        Sanitises the field value.
        :param value: The value to sanitise.
        :return: The list of values and the warning message.
        """
        self.logger.debug(f"Sanitising value {value}")
        message = None
        values = self.get_default_value()

        # check values
        if not value:
            self.logger.debug("The value is not provided")
        elif not isinstance(value, list):
            message = "The value provided in the model configuration is not valid"
            self.logger.debug(message)
        elif isinstance(value, list) and len(value) != 2:
            message = (
                "The value provided in the model configuration must contains "
                + "two values"
            )
            self.logger.debug(message)
        else:
            values = value

        return values, message

    def get_default_value(self) -> list[None]:
        """
        The field default value.
        :return: A list with two Nones.
        """
        return [None, None]

    def get_value(self) -> list[float]:
        """
        Returns the values when the predicate is false and true.
        :return: A list with the values.
        """
        values = []
        for spin_box in self.spin_boxes:
            values.append(spin_box.value())
        return values

    def reset(self) -> None:
        """
        Resets the widget values.
        :return: Sets the line edits value to zero.
        """
        for spin_box in self.spin_boxes:
            spin_box.setValue(0)
