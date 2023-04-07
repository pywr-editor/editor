import pytest
from PySide6.QtTest import QSignalSpy

from pywr_editor.widgets import CheckableComboBox


class TestCheckableComboBox:
    @pytest.mark.parametrize(
        "emit_signal",
        [False, True],
    )
    def test_add_items(self, qtbot, emit_signal):
        """
        Tests the addItems method. When adding multiple items, the signal is
        """
        items = ["Column 1", "Column 2", "Column 3"]
        combo_box = CheckableComboBox()
        qtbot.add_widget(combo_box)

        # noinspection PyTypeChecker
        spy = QSignalSpy(combo_box.model().dataChanged)
        combo_box.addItems(items, emit_signal=emit_signal)
        assert combo_box.all_items == items

        if emit_signal is True:
            assert spy.count() == 1
        else:
            assert spy.count() == 0

    @pytest.mark.parametrize(
        "items_to_check, emit_signal",
        [
            # integers
            [[1, 2], False],
            # different order
            [[2, 1], False],
            # same as above but signal is emitted
            [[1, 2], True],
            [[2, 1], True],
        ],
    )
    def test_check_items(self, qtbot, items_to_check, emit_signal):
        """
        Tests the check_items method.
        """
        expected = ["Column 2", "Column 3"]
        combo_box = CheckableComboBox()
        qtbot.add_widget(combo_box)

        # noinspection PyTypeChecker
        spy = QSignalSpy(combo_box.model().dataChanged)
        combo_box.addItems(["Column 1", "Column 2", "Column 3"])

        combo_box.check_items(items_to_check, emit_signal=emit_signal)
        assert combo_box.checked_items() == expected
        # line edit is always changed regardless of the Signal being emitted
        assert combo_box.lineEdit().text() == ", ".join(expected)

        if emit_signal is True:
            assert spy.count() == 1
        else:
            assert spy.count() == 0

        # reset and re-populate field
        new_items = ["Column X", "Column Y", "Column Z"]
        selected = 0
        combo_box.clear()
        combo_box.addItems(new_items)
        combo_box.check_items(selected, emit_signal=emit_signal)
        assert combo_box.checked_items() == [new_items[selected]]
        assert combo_box.lineEdit().text() == new_items[selected]
        if emit_signal is True:
            assert spy.count() == 2
        else:
            assert spy.count() == 0

    def test_uncheck_all(self, qtbot):
        """
        Tests the uncheck_all method.
        """
        combo_box = CheckableComboBox()
        qtbot.add_widget(combo_box)

        # noinspection PyTypeChecker
        spy = QSignalSpy(combo_box.model().dataChanged)
        combo_box.addItems(["Column 1", "Column 2", "Column 3"])

        combo_box.check_items([1, 2])
        assert spy.count() == 1
        combo_box.uncheck_all()
        assert spy.count() == 2
