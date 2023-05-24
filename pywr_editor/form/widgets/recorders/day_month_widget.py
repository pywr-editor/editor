from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from pywr_editor.form import FormCustomWidget, FormField, Validation
from pywr_editor.utils import Logging
from pywr_editor.widgets import SpinBox

"""
 Displays a widget with a day and month fields.
"""


class DayMonthWidget(FormCustomWidget):
    def __init__(self, name: str, value: dict[str, int | None], parent: FormField):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: A dictionary with the "day" and "month" keys, containing
        the set day and month.
        :param parent: The parent widget.
        """
        self.logger = Logging().logger(self.__class__.__name__)
        self.logger.debug(f"Loading widget {name} with value {value}")

        super().__init__(name, value, parent)

        day, month, self.warning_message = self.sanitise_values(value)

        self.day_spinbox = SpinBox()
        self.day_spinbox.setMinimum(0)
        self.day_spinbox.setMaximumWidth(80)
        self.day_spinbox.setValue(day)

        self.month_spinbox = SpinBox()
        self.month_spinbox.setMinimum(0)
        self.month_spinbox.setMaximumWidth(80)
        self.month_spinbox.setValue(month)

        # day layout
        layout_day = QVBoxLayout()
        layout_day.setContentsMargins(0, 0, 0, 0)
        layout_day.addWidget(QLabel("Day"))
        layout_day.addWidget(self.day_spinbox)

        # month layout
        layout_month = QVBoxLayout()
        layout_month.setContentsMargins(0, 0, 0, 0)
        layout_month.addWidget(QLabel("Month"))
        layout_month.addWidget(self.month_spinbox)

        # main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(layout_day)
        layout.addLayout(layout_month)
        layout.addStretch()

        self.form.register_after_render_action(self.register_actions)

    def register_actions(self) -> None:
        """
        Additional actions to perform after the widget has been added to the form
        layout.
        :return: None
        """
        self.logger.debug("Registering post-render section actions")
        self.field.set_warning(self.warning_message)

        if self.warning_message:
            self.logger.debug(self.warning_message)

    def sanitise_values(self, values: dict[str, int | None]) -> [int, int, str | None]:
        """
        Sanitises the values.
        :param values: A dictionary with the day and month.
        :return: The day, month and warning message.
        """
        self.logger.debug(f"Sanitising value {values}")

        day = 0
        month = 0
        warning_message = None

        if not values["day"] and not values["month"]:
            self.logger.debug("Both values are not provided")
        # day is provided, month is not
        elif values["day"] and not values["month"]:
            warning_message = "You must provide the month"
        # month is provided, day is not
        elif not values["day"] and values["month"]:
            warning_message = "You must provide the day"
        # check types
        elif not isinstance(values["day"], int) or not (1 <= values["day"] <= 31):
            warning_message = "The day must be a number between 1 and 31"
        elif not isinstance(values["month"], int) or not (1 <= values["month"] <= 12):
            warning_message = "The month must be a number between 1 and 12"
        else:
            day = values["day"]
            month = values["month"]

        return day, month, warning_message

    def get_value(self) -> dict[str | int]:
        """
        Returns the widget value.
        :return: A dictionary with the "day" and "month" keys, containing
        the set value and key.
        """
        return {
            "day": self.day_spinbox.value(),
            "month": self.month_spinbox.value(),
        }

    def get_default_value(self) -> dict[str | int]:
        """
        Returns the default value.
        :return: A dictionary with the day and month set to zero.
        """
        return {"day": 0, "month": 0}

    def validate(self, name: str, label: str, value: dict[str | int]) -> Validation:
        """
        :param name: The field name.
        :param label: The field label.
        :param value: The field value.
        :return: The Validation instance.
        """
        if value["day"] == 0 and value["month"] > 0:
            return Validation("You must provide the day, when you set the month")
        elif value["day"] > 0 and value["month"] == 0:
            return Validation("You must provide the month, when you set the day")
        return Validation()

    def after_validate(self, form_dict: dict, form_field_name: str) -> None:
        """
        Unpacks the day and month fields into the form dictionary.
        :param form_dict: The form dictionary.:
        :param form_field_name: The FormField name.
        :return: None
        """
        values = form_dict[form_field_name]
        # remove key if both values are zero
        if values == self.get_default_value():
            del form_dict[form_field_name]
            return

        for name, value in values.items():
            form_dict[f"{form_field_name}_{name}"] = value
        del form_dict[form_field_name]

    def reset(self) -> None:
        """
        Resets the widget.
        :return: Set zeros in both fields.
        """
        self.day_spinbox.setValue(0)
        self.month_spinbox.setValue(0)
