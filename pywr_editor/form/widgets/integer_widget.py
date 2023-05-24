from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout

from pywr_editor.form import FormCustomWidget, FormField
from pywr_editor.widgets import SpinBox


class IntegerWidget(FormCustomWidget):
    def __init__(
        self,
        name: str,
        value: int | None,
        parent: FormField,
        min_value: int | None = None,
        max_value: int | None = None,
        suffix: str | None = None,
    ):
        """
        Initialise a spin box to input integer numbers.
        :param name: The field name.
        :param value: The field value.
        :param parent: The parent field
        :param min_value: The minimum value. Optional
        :param max_value: The maximum value. Optional
        :param suffix: The suffix to use in the SpinBox. Optional.
        """
        super().__init__(name, value, parent)

        self.spin_box = SpinBox()
        self.field_value_changed: Signal = self.spin_box.textChanged

        # noinspection PyTypeChecker
        if min_value is not None and isinstance(min_value, int):
            self.spin_box.setMinimum(min_value)
        if max_value is not None and isinstance(max_value, int):
            self.spin_box.setMaximum(max_value)
        if suffix is not None and isinstance(suffix, str):
            self.spin_box.setSuffix(f" {suffix}")

        if value is not None and isinstance(value, int):
            if min_value and value < min_value:
                self.field.set_warning(
                    f"The provided value ({value}) must be larger than the minimum "
                    f"({min_value})"
                )
            elif max_value and value > max_value:
                self.field.set_warning(
                    f"The provided value ({value}) must be smaller than the maximum "
                    f"({max_value})"
                )
            self.spin_box.setValue(value)
        elif self.field.default_value is not None and isinstance(
            self.field.default_value, int
        ):
            self.spin_box.setValue(self.field.default_value)
        elif min_value is not None:
            self.spin_box.setValue(min_value)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.spin_box)
        layout.addStretch()

    def get_value(self) -> int:
        """
        Return the value in the SpinBox.
        :return: The set value.
        """
        return self.spin_box.value()
