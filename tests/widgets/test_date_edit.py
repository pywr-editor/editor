import pytest

from pywr_editor.widgets import DateEdit


@pytest.mark.parametrize(
    "date, expected",
    [
        ("2000-01-01", "01/01/2000"),
        ((2000, 1, 1), "01/01/2000"),
        (None, "01/01/2000"),
    ],
)
def test_date_edit(qtbot, date, expected):
    widget = DateEdit(date)
    assert expected == widget.date().toString("dd/MM/yyyy")
