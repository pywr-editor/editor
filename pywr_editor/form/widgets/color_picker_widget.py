from typing import Sequence

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QHBoxLayout, QWidget

from pywr_editor.form import FormCustomWidget, FormField
from pywr_editor.widgets import PushButton


class ColorPickerWidget(FormCustomWidget):
    """
    This form widget renders a widget showing the selected colour and allows the user to
    the select another colour using the system color picker dialog.
    """

    changed_color = Signal()
    """ signal emitted when a new colour is selected """

    def __init__(
        self,
        name: str,
        value: Sequence[int],
        parent: FormField,
        default_color: Sequence[int] = (0, 0, 0),
    ):
        """
        Initialise the widget.
        :param name: The field name.
        :param value: The colour as list of RGB values.
        :param parent: The parent widget.
        :param default_color: The default colour to use if the selected colour is not
        valid.
        """
        super().__init__(name, value, parent)

        # set default color
        self.default_color = default_color
        if (
            not isinstance(self.default_color, (list, tuple))
            or len(self.default_color) != 3
            or not QColor(*self.default_color).isValid()
        ):
            raise ValueError(
                "The default_color must be a sequence of three integers"
            )

        # set selected color
        self.sanitise_color()
        self.preview_color_box = QWidget()
        self.preview_color_box.setFixedSize(30, 30)
        self.set_preview_color(self.value)

        button = PushButton("Select colour")
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.open_color_picker)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 5, 0)
        layout.addWidget(self.preview_color_box)
        layout.addWidget(button)
        layout.addStretch()
        self.setLayout(layout)

    def sanitise_color(self) -> None:
        """
        Sanitise the color. The color must be a sequence with three items
        with the RGB values. If this is not the case, a default colour us used.
        :return: None
        """
        if (
            not isinstance(self.value, (list, tuple))
            or len(self.value) != 3
            or not QColor(*self.value).isValid()
        ):
            self.value = self.default_color

    def set_preview_color(self, color: Sequence[int]) -> None:
        """
        Set the selected colour on the preview box.
        :param color: The colour as RGB values.
        :return: None
        """
        self.preview_color_box.setStyleSheet(
            f"background: rgb({color[0]}, {color[1]}, {color[2]});"
            + "border: 1px solid #CCC; border-radius: 5px;"
        )

    @Slot()
    def open_color_picker(self) -> None:
        """
        Open the colour picker.
        :return: None
        """
        dialog = QColorDialog()
        color = dialog.getColor(
            initial=QColor.fromRgb(*self.value), parent=self
        )
        # convert to RGB
        if color.isValid():
            self.value = color.toTuple()[0:3]
            self.set_preview_color(self.value)
            self.changed_color.emit()

    def get_value(self) -> Sequence[int]:
        """
        Returns the selected colour.
        :return: The colour as listr of RGB values.
        """
        return self.value
