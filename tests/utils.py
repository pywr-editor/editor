from pathlib import Path

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget

from pywr_editor.widgets import TableView


def model_path() -> Path:
    """
    Returns the full path to the folder containing the JSON files.
    :return: The Path instance to the folder with the test models.
    """
    return Path(__file__).parent.absolute() / "json_models"


def resolve_model_path(file_name: str) -> str:
    """
    Returns the full path to the model file.
    :param file_name: The model file name.
    :return: The path to the JSON file.
    """
    return str(model_path() / file_name)


def close_message_box(parent: QWidget = None):
    """
    Closes the message box.
    :param parent: The parent widget where to look for the QMessageBox. When None, the
    message box is assumed to be the active modal widget. Default to None.
    :return: None
    """
    if parent is None:
        widget = QApplication.activeModalWidget()
        if widget is not None and isinstance(widget, QMessageBox):
            widget.close()
    else:
        # noinspection PyTypeChecker
        widget: QMessageBox = parent.findChild(QMessageBox)
        if widget is not None:
            widget.close()


def check_msg(message: str):
    """
    Asserts that the message box has the given message.
    :param message: The message to check.
    :return: None
    """
    if message is None:
        assert True
        return

    widget: QMessageBox = QApplication.activeModalWidget()

    if widget is not None:
        text = widget.text()
        assert message in text
        widget.close()
    else:
        assert False, f"QMessageBox not found. Message was '{message}'"


def change_table_view_cell(
    qtbot,
    table: TableView,
    row: int,
    column: int,
    old_name: str,
    new_name: str | int,
) -> None:
    """
    Change the value in a TableView cell.
    :param qtbot: The qtbot instance.
    :param table: The TableView instance.
    :param row: The row index.
    :param column: The column index.
    :param old_name: The name set in the cell.
    :param new_name: The new name to set.
    :return: None
    """
    x = table.columnViewportPosition(column) + 5
    y = table.rowViewportPosition(row) + 10
    old_model_name = table.model.data(
        table.model.index(row, column), Qt.ItemDataRole.DisplayRole
    )

    assert (
        old_model_name == old_name
    ), f"Expected '{old_name}', got '{old_model_name}'"

    qtbot.mouseClick(
        table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
    )
    qtbot.mouseDClick(
        table.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, y)
    )
    qtbot.keyClick(table.viewport().focusWidget(), Qt.Key_Backspace)
    for letter in list(str(new_name)):
        if letter == "":
            continue
        if letter == "_":
            key = Qt.Key_Underscore
        else:
            key = getattr(Qt, f"Key_{letter.title()}")

        qtbot.keyClick(table.viewport().focusWidget(), key)
    qtbot.keyClick(table.viewport().focusWidget(), Qt.Key_Enter)
    qtbot.wait(100)
