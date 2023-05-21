import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QValidator

from pywr_editor.widgets import DoubleSpinBox


class TestDoubleSpinBox:
    @pytest.mark.parametrize(
        "value, spin_box_kargs",
        [
            (4 * pow(10, 5), {}),
            (4 * pow(10, -3), {}),
            (-4 * pow(10, 4), {}),
            (1000.900100, {}),
            (
                4 * pow(10, -5),
                {
                    "precision": 6,
                    "lower_bound": -pow(10, 6),
                    "upper_bound": pow(10, 6),
                },
            ),
            (0.105600, {}),
            # value set to default
            (3.1 * pow(10, 25), {}),
            (-3.1 * pow(10, 25), {}),
            # reduced precision
            (1 * pow(10, -5), {"precision": 2}),
        ],
    )
    def test_scientific_notation_init(self, qtbot, value, spin_box_kargs):
        """
        Tests that the widget returns the correct number and shows the right string
        representation.
        """
        spin_box = DoubleSpinBox(
            parent=None, scientific_notation=True, **spin_box_kargs
        )
        spin_box.setValue(value)
        spinbox_lb = spin_box.minimum()
        spinbox_ub = spin_box.maximum()

        qtbot.addWidget(spin_box)

        # upper bound set to default, but number is larger
        if "upper_bound" not in spin_box_kargs and value > spinbox_ub:
            value = spinbox_ub
        if "lower_bound" not in spin_box_kargs and value < spinbox_lb:
            value = spinbox_lb
        if "precision" in spin_box_kargs:
            value = round(value, spin_box_kargs["precision"])

        assert spin_box.value() == value
        assert spin_box.lineEdit().text() == f"{value:e}"

    @pytest.mark.parametrize(
        "spin_box_kargs",
        [
            {"upper_bound": pow(10, 11)},
            {"lower_bound": -pow(10, 15)},
            {"precision": 23},
        ],
    )
    def test_scientific_notation_exception(self, qtbot, spin_box_kargs):
        """
        Tests that the widget rises an exception if the bounds or precision are too
        large.
        """
        with pytest.raises(ValueError):
            DoubleSpinBox(parent=None, **spin_box_kargs)

    @pytest.mark.parametrize(
        "text_to_input, spin_box_kargs, validated",
        [
            ("123e-5", {}, True),
            ("1.54323e6", {}, True),
            ("1.54323e26", {"upper_bound": pow(10, 30)}, True),
            (
                "1.54323e-26",
                {"lower_bound": -pow(10, 25)},
                True,
            ),
            ("e5", {}, False),
            ("1000", {"upper_bound": pow(10, 3)}, True),
            ("0.0032", {}, True),
        ],
    )
    def test_spin_box_set_new_value(
        self, qtbot, text_to_input, spin_box_kargs, validated
    ):
        """
        Tests the widget accepts number written in scientific notation and that the
        number properly is saved.
        """
        spin_box = DoubleSpinBox(
            parent=None, scientific_notation=True, precision=7, **spin_box_kargs
        )
        spinbox_lb = spin_box.minimum()
        spinbox_ub = spin_box.maximum()
        line_edit = spin_box.lineEdit()
        line_edit.clear()

        # Start editing the text
        qtbot.mouseClick(line_edit, Qt.MouseButton.LeftButton)

        # Check that e, e+ and e- are accepted. Input text one number at the time to
        # mimic user's behaviour
        partial_text = ""
        for ch in text_to_input:
            qtbot.keyClick(line_edit, ch)
            partial_text += ch
            assert line_edit.text() == partial_text
            assert spin_box.validate(partial_text, 0)[0] == QValidator.State.Acceptable

        # confirm value to show string
        qtbot.keyClick(line_edit, Qt.Key_Enter)

        if validated:
            # add trailing zeros before e sign
            text_to_float = float(text_to_input)
            # upper bound set to default, but number is larger
            if (
                "upper_bound" not in spin_box_kargs
                and float(text_to_input) > spinbox_ub
            ):
                text_to_float = spinbox_ub
            if (
                "lower_bound" not in spin_box_kargs
                and float(text_to_input) < spinbox_lb
            ):
                text_to_float = spinbox_lb

            assert spin_box.lineEdit().text() == f"{text_to_float:e}"
            assert spin_box.value() == text_to_float
        else:
            assert spin_box.lineEdit().text() == f"{0:e}"
            assert spin_box.value() == 0
