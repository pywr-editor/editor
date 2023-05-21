from typing import Sequence

import qtawesome as qta
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QHBoxLayout, QWidget

from pywr_editor.form import FormCustomWidget, FormField
from pywr_editor.widgets import PushIconButton


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
        enable_alpha: bool = False,
    ):
        """
        Initialise the widget.
        :param name: The field name.
        :param value: The colour as list of RGB values.
        :param parent: The parent widget.
        :param default_color: The default colour to use if the selected colour is not
        valid.
        :param enable_alpha: Whether to enable the alpha channel for the colour.
        Default to False.
        """
        super().__init__(name, value, parent)

        # set default color
        self.default_color = default_color
        self.enable_alpha = enable_alpha
        if (
            not isinstance(self.default_color, (list, tuple))
            or len(self.default_color) <= 2
            or not QColor(*self.default_color).isValid()
        ):
            raise ValueError("The default_color must be a sequence of three integers")

        # set selected color
        self.sanitise_color()
        self.preview_color_box = QWidget()
        self.preview_color_box.setFixedSize(30, 30)
        self.set_preview_color(self.value)

        button = PushIconButton(
            icon=qta.icon("msc.symbol-color"), label="Select colour"
        )
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
            or len(self.value) <= 2
            or not QColor(*self.value).isValid()
        ):
            self.value = self.default_color

    def set_preview_color(self, color: Sequence[int]) -> None:
        """
        Set the selected colour on the preview box.
        :param color: The colour as RGB values.
        :return: None
        """

        if self.enable_alpha and len(color) == 4:
            rgb = f"rgba({color[0]}, {color[1]}, {color[2]}, {color[3]})"
        else:
            rgb = f"rgb({color[0]}, {color[1]}, {color[2]})"
        self.preview_color_box.setStyleSheet(
            f"background: {rgb}; border: 1px solid #CCC; border-radius: 5px;"
        )

    @Slot()
    def open_color_picker(self) -> None:
        """
        Open the colour picker.
        :return: None
        """
        dialog = QColorDialog()
        options = {
            "initial": QColor.fromRgb(*self.value),
            "parent": self,
        }
        if self.enable_alpha:
            options["options"] = QColorDialog.ColorDialogOption.ShowAlphaChannel
        color = dialog.getColor(**options)

        # convert to RGB
        if color.isValid():
            self.value = color.toTuple() if self.enable_alpha else color.toTuple()[0:3]
            self.set_preview_color(self.value)
            self.changed_color.emit()

    def get_value(self) -> Sequence[int]:
        """
        Returns the selected colour.
        :return: The colour as listr of RGB values.
        """
        return self.value
