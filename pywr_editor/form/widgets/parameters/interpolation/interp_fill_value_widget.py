from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import AbstractFloatListWidget, FormField, FormValidation
from pywr_editor.utils import get_signal_sender
from pywr_editor.widgets import ComboBox

"""
 Defines a widget to select the extrapolation options:
  - no extrapolation
  - extrapolation (extrapolate option scipy.interpolate.interp1d)
  - provides the value to use when x is outside the lower
    and upper interpolation bounds (fill_value option of
    scipy.interpolate.interp1d)
"""


class InterpFillValueWidget(AbstractFloatListWidget):
    labels_map = {
        "no_extrapolation": "Do not extrapolate",
        "fill": "Fill with values",
        "extrapolate": "Extrapolate",
    }

    def __init__(
        self,
        name: str,
        value: str | list[float | int] | int | float | None,
        parent: FormField = None,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected parameter name.
        :param parent: The parent widget.
        """
        self.raw_value = value

        # if value is a number, force it to list
        if isinstance(value, (float, int)) and not isinstance(value, bool):
            value = [value, value]

        super().__init__(
            name=name,
            value=value,
            parent=parent,
            items_count=2,
            allowed_empty=False,
            only_list=True,
            log_name=self.__class__.__name__,
        )

        # Add the ComboBox with choices
        self.combo_box = ComboBox()
        self.combo_box.addItems(list(self.labels_map.values()))
        # noinspection PyUnresolvedReferences
        self.combo_box.currentIndexChanged.connect(self.on_update_value)

        # add ComboBox
        # noinspection PyTypeChecker
        layout: QHBoxLayout = self.findChild(QHBoxLayout)
        layout.insertWidget(0, self.combo_box)
        layout.addStretch()

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        # Init parent widget
        super().register_actions()
        # SHow/hide QLineEdit
        self.on_update_value()

        # empty string or value not provided
        if self.raw_value is None or self.raw_value == "":
            self.logger.debug("Setting no extrapolation")
            self.combo_box.setCurrentText(self.labels_map["no_extrapolation"])
            # reset warning from parent widget and hide QLineEdit
            self.form_field.clear_message()
        # value is string, check for correct keyword
        elif isinstance(self.raw_value, str):
            self.logger.debug("Setting extrapolation")
            # reset warning from parent widget and hide QLineEdit
            self.form_field.clear_message()

            self.combo_box.setCurrentText(self.labels_map["extrapolate"])
            # show error if value is wrong
            if self.raw_value.lower() != "extrapolate":
                message = "The value set in the model configuration is not valid"
                self.logger.debug(message)
                self.form_field.set_warning_message(message)
        # default to parent widget - fill with values
        else:
            self.combo_box.setCurrentText(self.labels_map["fill"])

    @Slot()
    def on_update_value(self) -> None:
        """
        Shows or hides the QLineEdit field based on the selected value in the ComboBox.
        :return: None
        """
        self.logger.debug(
            f"Running on_update_value Slot from {get_signal_sender(self)}"
        )
        self.line_edit.setVisible(
            self.combo_box.currentText() == self.labels_map["fill"]
        )

    def get_value(self) -> str | list[float | int] | None:
        """
        Returns the value.
        :return: The list of values or the "extrapolate" string or None.
        """
        option = self.combo_box.currentText()
        if option == self.labels_map["no_extrapolation"]:
            return None
        elif option == self.labels_map["fill"]:
            return super().get_value()
        # extrapolate
        else:
            return "extrapolate"

    def validate(
        self, name: str, label: str, value: str | list[float | int] | None
    ) -> FormValidation:
        """
        Checks that the value is valid.
        :param name: The field name.
        :param label: The field label.
        :param value: The field label. This is not used.
        :return: The FormValidation instance.
        """
        if self.combo_box.currentText() == self.labels_map["fill"]:
            self.logger.debug(f"Validation with {self.labels_map['fill']}")
            return super().validate(name, label, value)

        # other options do not need validation
        return FormValidation(validation=True)

    def reset(self) -> None:
        """
        Resets the widget. This empties the QLineEdit widget and restore the method to
        "Fill with values".
        :return: None
        """
        super().reset()
        self.combo_box.setCurrentText(self.labels_map["no_extrapolation"])
