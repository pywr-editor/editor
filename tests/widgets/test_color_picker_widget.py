from typing import Sequence

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QColorDialog, QPushButton, QSpinBox, QWidget

from pywr_editor.form import ColorPickerWidget, Form
from pywr_editor.utils import is_windows
from pywr_editor.widgets import PushIconButton


class TestColorPickerWidget:
    @staticmethod
    def widget(selected_color: Sequence[int] | None) -> ColorPickerWidget:
        """
        Initialises the form and returns the widget.
        :param selected_color: The selected RGB colour.
        :return: An instance of ColorPickerWidget.
        """
        form = Form(
            available_fields={
                "Section": [
                    {
                        "name": "colour",
                        "field_type": ColorPickerWidget,
                        "value": selected_color,
                    }
                ]
            },
            save_button=QPushButton("Save"),
            parent=QWidget(),
        )
        form.enable_optimisation_section = False
        form.load_fields()

        form_field = form.find_field_by_name("colour")
        return form_field.widget

    @pytest.mark.parametrize(
        "selected_color, is_valid",
        [
            # invalid colours
            (None, False),
            ("red", False),
            ([0, 0], False),
            ([2000, 200, 100], False),
            # valid colour
            ([125, 125, 125], True),
        ],
    )
    def test_init(self, qtbot, selected_color, is_valid):
        """
        Test when the widget is initialised.
        """
        widget = self.widget(selected_color)
        # correct value is selected
        if is_valid:
            color = selected_color
        else:
            color = widget.default_color
        assert widget.value == color
        assert widget.get_value() == color

        # check preview colour box
        assert f"{tuple(color)}" in widget.preview_color_box.styleSheet()
        new_color_value = 125

        def set_color():
            """
            Selects a new colour using the Windows color picker.
            """
            # noinspection PyTypeChecker
            w: QColorDialog = widget.findChild(QColorDialog)

            # select colour
            for spin_box in w.findChildren(QSpinBox)[3:]:
                spin_box.setValue(new_color_value)

            # confirm selection
            # noinspection PyUnresolvedReferences
            ok_button: QPushButton = w.findChildren(QPushButton)[2]
            assert ok_button.text() == "OK"
            qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)

        # select new colour
        if is_windows():
            spy = QSignalSpy(widget.changed_color)

            QTimer.singleShot(200, set_color)
            qtbot.mouseClick(
                widget.findChild(PushIconButton), Qt.MouseButton.LeftButton
            )
            new_color_rgb = tuple([new_color_value] * 3)
            assert widget.get_value() == new_color_rgb
            assert spy.count() == 1
            assert f"{new_color_rgb}" in widget.preview_color_box.styleSheet()
