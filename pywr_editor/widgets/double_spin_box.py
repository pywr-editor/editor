import re
import PySide6
from PySide6.QtCore import Qt
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QDoubleSpinBox, QWidget


class DoubleSpinBox(QDoubleSpinBox):
    def __init__(
        self,
        lower_bound: float = -pow(10, 6),
        upper_bound: float = pow(10, 6),
        precision: int = 4,
        scientific_notation: bool = False,
        parent: QWidget = None,
    ):
        """
        Initialises the widget to create a QDoubleSpinBox with new limits and precision.
        :param lower_bound: The allowed minimum number. Default to -10^6
        :param upper_bound: The allowed maximum number. Default to 10^6
        :param precision: The precision. Default to 4.
        :param scientific_notation: Enable scientific notation. All numbers will be
        shown using scientific notation and user can input number in the same format
        as well.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.scientific_notation = scientific_notation

        if (
            lower_bound < -pow(10, 10)
            or upper_bound > pow(10, 10)
            or precision > 8
        ) and not self.scientific_notation:
            raise ValueError(
                "Scientific notation is not on. To represent large numbers and "
                "to avoid these being approximated, set scientific_notation to True"
            )

        self.setRange(float(lower_bound), float(upper_bound))
        self.setDecimals(precision)
        # prevent mouse wheel from changing value on scroll
        self.setFocusPolicy(Qt.StrongFocus)

    def validate(self, text: str, pos: int) -> [QValidator.State, str, int]:
        """
        Validates the text input in the QLineEdit.
        :param text: The text.
        :param pos: The position.
        :return: A tuple with whether the text is accepted, the text and position.
        """
        # check if user is typing e+ or e-
        if self.scientific_notation and "e" in text.lower():
            if re.search(r"^[+-]?\d*(\.\d+)?([+-][eE]\d+)?", text):
                return QValidator.State.Acceptable, text, pos
            else:
                return QValidator.State.Invalid, text, pos

        return super().validate(text, pos)

    def valueFromText(self, text: str) -> float:
        """
        When scientific notation is on, convert strings given with SN
        to the correct number.
        :param text: The text in the QLineEdit field of the QDoubleSpinBox.
        :return: The number.
        """
        if not self.scientific_notation:
            return super().valueFromText(text)

        # as user is typing e- or e+, float will fail until the complete number is
        # typed. If the number is not complete and the user press enter, return 0
        try:
            return float(text)
        except ValueError:
            return 0

    def textFromValue(self, value: float) -> str:
        """
        Converts the number to string to be displayed in the QLineEdit field of the
        QDoubleSpinBox.
        :param value: The number.
        :return: The string representation of the number.
        """
        if not self.scientific_notation:
            return super().textFromValue(value)

        return f"{value:e}"

    def wheelEvent(self, e: PySide6.QtGui.QWheelEvent) -> None:
        """
        Prevents user from changing the value on scroll.
        :param e: The event being triggered.
        :return: None
        """
        if self.hasFocus():
            super().wheelEvent(e)
        else:
            e.ignore()
