import platform
import sys
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QWidget


def humanise_label(key: str) -> str:
    """
    Returns a human-readable version of a label. For example "minimum_version"
    is converted to "Minimum version".
    :param key: The label to convert.
    :return: The converted string.
    """
    key = str(key).replace("_", " ")
    key = "{}{}".format(key[0].upper(), key[1:])
    return key


def label_to_key(label: str) -> str:
    """
    Converts a human-readable string to a key. For example "Minimum version"
    is converted to "minimum_version".
    :param label: The label to convert.
    :return: The key.
    """
    return str(label).replace(" ", "_").lower().strip()


def is_windows() -> bool:
    """
    Returns True if the editor is run on Windows.
    :return: True if the platform is Windows, False otherwise.
    """
    return platform.system() == "Windows"


def is_excel_installed(winapi: bool = False) -> bool:
    """
    Returns True if Microsoft Excel is installed on Windows by checking if EXCEL.EXE
    exist.
    :param winapi: Whether to use the WIN32 API to test if Excel is installed and can
    run. This method is slower.
    :return: True if Excel is installed, False otherwise.
    """
    if not winapi:
        return Path(
            r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE"
        ).exists()

    import win32com.client

    # noinspection PyBroadException
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        _ = excel.version
        excel.Quit()
        return True
    except Exception:
        return False


def is_app_frozen() -> bool:
    """
    Returns True if the app was frozen with PyInstaller.
    :return: Whether the app is frozen.
    """
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_app_path() -> Path:
    """
    Returns the path where the application is executed.
    :return: The Path instance of the application.
    """
    if is_app_frozen():
        # noinspection PyProtectedMember
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent.parent.parent


def maybe_delete_component(
    component_name: str, total_times: int, parent: QWidget
) -> bool:
    """
    Asks user if they want to delete a component that's being used.
    :param component_name: The component name to delete.
    :param total_times: The number of times the component is used by the model.
    :param parent: The parent widget.
    :return: True whether to delete the component, False otherwise.
    """
    message = "Do you want to delete the selected item?"
    if total_times > 0:
        times = "time"
        if total_times > 1:
            times = f"{times}s"
        message = (
            f"The item you would like to delete is used {total_times} "
            + f"{times} by other model components. If you delete it, the "
            + "model will not be able to run anymore.\n\n"
            + "Do you want to continue?"
        )

    answer = QMessageBox.warning(
        parent,
        "Warning",
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    if answer == QMessageBox.StandardButton.Yes:
        return True
    elif answer == QMessageBox.StandardButton.No:
        return False
    # on discard
    return False
