from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

# noinspection PyUnresolvedReferences
from .assets import *
from .color import Color


def stylesheet_dict_to_str(stylesheet: dict, root_selector: str = "") -> str:
    """
    Converts a dictionary representing a stylesheet to a string. This supports nested
    dictionary as well.
    :param stylesheet: The stylesheet as dictionary. The key is the selector and the
    value a dictionary with the CSS properties as keys and their values as values.
    :param root_selector: The root selector if available.
    :return: The CSS as string.
    """
    stylesheet_str = ""

    for key, value in stylesheet.items():
        if hasattr(value, "items"):
            if len(root_selector) > 0:
                stylesheet_str += "}\n"
                if ":" in key:
                    stylesheet_str += f"{root_selector}{key} {{\n"
                else:
                    stylesheet_str += f"{root_selector} {key} {{\n"
            else:
                stylesheet_str += f"{key} {{\n"

            if ":" in key:
                new_root = root_selector + key
            else:
                new_root = f"{root_selector} {key}"

            stylesheet_str += stylesheet_dict_to_str(value, new_root.strip())
            if len(root_selector) == 0:
                stylesheet_str += "}\n"
        else:
            stylesheet_str += f"\t{key}: {value};\n"

    return stylesheet_str


class AppStylesheet:
    def __init__(self):
        """
        Sets the font.
        """
        db = QFontDatabase.font("Segoe UI", "", 12)
        if db.exactMatch():
            font = QFont("Segoe UI", 10)
            QApplication.setFont(font)

    def get(self) -> str:
        """
        Returns the application stylesheet.
        :return: The stylesheet as string.
        """
        return stylesheet_dict_to_str(
            {
                **self.buttons,
                **self.forms,
                **self.scrollbar,
                **self.misc,
            }
        )

    @property
    def misc(self) -> dict:
        """
        Returns the style for the miscellaneous components.
        :return: The stylesheet dictionary.
        """
        return {
            "QMainWindow": {
                "background": Color("neutral", 100).hex,
            },
            "QStatusBar": {
                "background": Color("neutral", 200).hex,
                "color": Color("neutral", 600).hex,
            },
            "QToolTip": {
                "background": Color("neutral", 100).hex,
                "border": f"1px solid{Color('neutral', 300).hex}",
                "color": Color("neutral", 600).hex,
            },
        }

    @property
    def forms(self) -> dict:
        """
        Returns the style for the forms.
        :return: The stylesheet dictionary.
        """
        spin_box = {
            "padding-right": "15px",
            "border-width": "3",
            "background": "#FFF",
            "border": f"1px solid {Color('neutral', 300).hex}",
            "border-radius": "4px",
            "padding": "5px 6px",
            ":hover": {
                "background": Color("neutral", 100).hex,
            },
            ":focus": {
                "border": f"1px solid {Color('blue', 400).hex}",
            },
            ":focus:hover": {
                "background": "#FFF",
            },
            "::up-button": {
                "subcontrol-origin": "border",
                "subcontrol-position": "top right",
                "border-width": "1px",
            },
            "::down-button": {
                "subcontrol-origin": "border",
                "subcontrol-position": "bottom right",
                "border-width": "1px",
                "border-top-width": "0",
            },
            "::up-arrow": {
                "border-image": "url(:form/caret-up)",
                "width": "10px",
                "height": "10px",
                "right": "3px",
                "top": "2px",
            },
            "::down-arrow": {
                "border-image": "url(:form/caret-down)",
                "width": "10px",
                "height": "10px",
                "right": "3px",
                "bottom": "2px",
            },
            "::up-arrow:disabled": {
                "border-image": "url(:form/caret-up-disabled)"
            },
            "::up-arrow:off": {"border-image": "url(:form/caret-up-disabled)"},
            "::down-arrow:disabled": {
                "border-image": "url(:form/caret-down-disabled)"
            },
            "::down-arrow:off": {
                "border-image": "url(:form/caret-down-disabled)"
            },
        }

        return {
            "QGroupBox": {
                "border": 0,
                "font-weight": "bold",
                "border-bottom": f"2px solid {Color('neutral', 200).hex}",
                "font-size": "15px",
                "margin-top": "15px",
                "padding": "7px 0px",
                ":title": {
                    "subcontrol-origin": "margin",
                    "top": "4px",
                    "left": "0px",
                    "padding": "0px 4px",
                    "subcontrol-position": "top left",
                },
            },
            "QPlainTextEdit": {
                "background": "#FFF",
                "border": f"1px solid {Color('neutral', 300).hex}",
                "border-radius": "4px",
            },
            "QLineEdit, QTextEdit": {
                "background": "#FFF",
                "border": f"1px solid {Color('neutral', 300).hex}",
                "border-radius": "4px",
                "padding": "5px 6px",
            },
            "QLineEdit:hover, QTextEdit:hover": {
                "background": Color("neutral", 50).hex,
            },
            "QLineEdit:focus, QTextEdit:focus": {
                "border": f"1px solid {Color('blue', 400).hex}",
            },
            "QLineEdit:focus:hover, QTextEdit:focus:hover": {
                "background": "#FFF",
            },
            "QDialog": {
                "background": Color("neutral", 100).hex,
                # "background": Color("neutral", 100).hex,
                "border": f"1px solid {Color('neutral', 300).hex}",
                # "background": Color("neutral", 50).hex,
                "color": Color("neutral", 600).hex,
            },
            "QGroupBox, QLabel": {
                "color": Color("neutral", 700).hex,
            },
            "SpinBox": spin_box,
            "DoubleSpinBox": spin_box,
        }

    @property
    def buttons(self) -> dict:
        """
        Returns the style for the buttons.
        :return: The stylesheet dictionary.
        """
        return {
            "QPushButton": {
                "background": "rgba(0, 0, 0, 7)",
                "border": "1px solid rgba(0, 0, 0, 20)",
                "border-radius": "4px",
                "padding": "6px 10px",
            },
            "QPushButton:pressed": {"color": "rgba(0, 0, 0, 150)"},
            "QPushButton:hover": {
                "background-color": "rgba(0, 0, 0, 20)",
                "border": "1px solid rgba(0, 0, 0, 28)",
            },
            "QPushButton:disabled": {
                "background": "rgba(0, 0, 0, 7)",
                "border": "1px solid rgba(0, 0, 0, 5)",
                "color": "rgba(0, 0, 0, 80)",
            },
            # PushIconButton
            "QPushButton QLabel:disabled": {
                "color": Color("neutral", 200).hex,
            },
            "QPushButton:focus": {
                "background-color": Color("blue", 100).hex,
            },
        }

    @property
    def scrollbar(self) -> dict:
        """
        Returns the style for the scrollbars.
        :return: The stylesheet dictionary.
        """
        return {
            "QScrollBar": {
                ":vertical": {
                    "background": "transparent",
                    "border": "6px solid rgba(0, 0, 0, 0)",
                    "margin": "14px 0px 10px 0px",
                    "width": "16px",
                },
                ":vertical:hover": {"border": "5px solid rgba(0, 0, 0, 0)"},
                ":horizontal": {
                    "background": "transparent",
                    "border": "6px solid rgba(0, 0, 0, 0)",
                    "margin": "0px 14px 0px 10px",
                    "height": "16px",
                },
                ":horizontal:hover": {"border": "5px solid rgba(0, 0, 0, 0)"},
                "::handle:vertical": {
                    "background-color": Color("neutral", 400).hex,
                    "border-radius": "2px",
                    "min-height": "25px",
                },
                "::handle:horizontal": {
                    "background-color": Color("neutral", 400).hex,
                    "border-radius": "2px",
                    "min-width": "25px",
                },
                # up and left arrows
                "::sub-line:vertical": {
                    "image": "url(:scrollbar/scroll-up)",
                    "margin-top": "5px",
                    "height": "10px",
                    "width": "10px",
                    "subcontrol-origin": "margin",
                    "subcontrol-position": "top",
                },
                "::sub-line:horizontal": {
                    "image": "url(:scrollbar/scroll-left)",
                    "height": "10px",
                    "width": "10px",
                    "subcontrol-origin": "margin",
                    "subcontrol-position": "left",
                },
                # # down and right arrow
                "::add-line:vertical": {
                    "height": "10px",
                    "width": "10px",
                    "image": "url(:scrollbar/scroll-down)",
                    "subcontrol-position": "bottom",
                    "subcontrol-origin": "margin",
                },
                "::add-line:horizontal": {
                    "height": "10px",
                    "width": "10px",
                    "image": "url(:scrollbar/scroll-right)",
                    "subcontrol-position": "right",
                    "subcontrol-origin": "margin",
                },
                # remove background from arrow containers
                "::add-page:vertical": {"background": "none"},
                "::add-page:horizontal": {"background": "none"},
                "::sub-page:vertical": {"background": "none"},
                "::sub-page:horizontal": {"background": "none"},
            },
        }
