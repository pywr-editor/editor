from pywr_editor.style import Color, stylesheet_dict_to_str


def about_dialog_stylesheet() -> str:
    """
    Defines the about dialog stylesheet.
    :return: The stylesheet as string.
    """
    style = {
        "QDialog": {
            "background-color": Color("gray", 100).hex,
            "border": f'1px solid {Color("neutral", 300).hex}',
        }
    }

    return stylesheet_dict_to_str(style)
