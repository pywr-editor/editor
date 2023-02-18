import platform
import sys
from pathlib import Path


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


def is_excel_installed() -> bool:
    """
    Returns True if Microsoft Excel is installed on Windows.
    This method is slow as it relies on the WIN32 API.
    :return: True if Excel is installed, False otherwise.
    """
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
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent.parent.parent
