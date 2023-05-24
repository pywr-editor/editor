from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy

from pywr_editor.form import FormCustomWidget, FormField
from pywr_editor.widgets import ToggleSwitchWidget


class BooleanWidget(FormCustomWidget):
    def __init__(self, name: str, value: int | None, parent: FormField):
        """
        Initialise a toggle switch.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent field.
        """
        super().__init__(name, value, parent)

        self.toggle = ToggleSwitchWidget()
        self.field_value_changed: Signal = self.toggle.stateChanged
        self.toggle.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)

        if self.field.default_value is not None and not isinstance(
            self.field.default_value, bool
        ):
            raise ValueError(f"default_value for '{name}' must be a boolean")
        if value is None or not isinstance(value, bool):  # use the default value
            self.toggle.setChecked(True if self.field.default_value else False)
        else:
            self.toggle.setChecked(value)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle)
        layout.addStretch()

    def get_value(self) -> int:
        """
        Return the value in the toggle.
        :return: The set value.
        """
        return self.toggle.isChecked()
