from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFileDialog, QWidget, QLayout


def clear_layout(layout: QLayout) -> None:
    """
    Removes all widgets and layouts belonging to the layout.
    :param layout: The layout instance.
    :return: None
    """
    if layout is None:
        return
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
            # noinspection PyTypeChecker
            child.widget().setParent(None)
        elif child.layout() is not None:
            clear_layout(child.layout())


def get_signal_sender(cls: QObject) -> str:
    """
    Returns a string with the class, name and triggered Signal of the sender.
    :param cls: The class instance of the Slot.
    :return: A string with the sender information.
    """
    sender = cls.sender()
    if sender is not None:
        meta_obj = sender.metaObject()
        meta_method = meta_obj.method(cls.senderSignalIndex())
        return (
            f"{meta_obj.className()}({sender.objectName()})."
            + f"{str(meta_method.name(), 'utf-8')}"
        )
    return "Direct Slot call"


def find_parent_by_name(widget: QWidget, name: str) -> QWidget:
    """
    Finds a parent widget by name.
    :param widget: The widget instance.
    :param name: The name of the parent (set in objectName())
    :return: The instance of the parent widget.
    """
    widget = widget.parentWidget()
    if widget and widget.objectName() != name:
        return find_parent_by_name(widget, name)
    return widget


def browse_files(file_filter: str = "JSON file (*.json)") -> None | str:
    """
    Opens the file browser and returns the selected file.
    :param file_filter: The filter to apply for the file extension.
    :return: The selected file. If multiple files are selected, only the
    first file is returned.
    """
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    file_dialog.setNameFilter(file_filter)
    file_dialog.exec()
    files = file_dialog.selectedFiles()
    if len(files) > 0:
        return files[0]
    else:
        return None
